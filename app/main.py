import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .errors import error_handler
import sys
import os
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry import trace as _otel_trace
from .logger import setup_logger, logger_middleware
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from .middlewares import timeout_middleware
from .adapters.httphandlers.product_handler import router as product_router
from .config import Container
import logging

logger = setup_logger(level=logging.INFO)

# Initialize and wire the dependency injection container
container = Container()
container.wire(modules=["app.adapters.httphandlers.product_handler"])

app = FastAPI(
    title="Products API",
    description="""
    ## Products Catalog API

    A comprehensive REST API for managing and retrieving product information across multiple categories including:
    - **Laptops** - Professional and gaming laptops with detailed specifications
    - **Smartphones** - Latest mobile devices with camera and performance specs  
    - **Headphones** - Audio devices with sound quality and feature details
    - **TVs** - Smart TVs with display technology and entertainment features

    ### Features
    - **Pagination Support** - Efficient data retrieval with customizable page sizes
    - **Rich Product Data** - Detailed specifications, ratings, and availability
    - **Performance Testing** - Optional delay parameter for load testing
    - **Comprehensive Filtering** - Category-based product organization

    ### Architecture
    Built using hexagonal architecture with clean separation of concerns, dependency injection, and comprehensive observability.
    """,
    version="1.0.0",
    contact={
        "name": "Products API Support",
        "email": "support@products-api.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:8080",  # Vue development server
        "http://localhost:4200",  # Angular development server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:4200",
        # Add your production domains here
        # "https://yourdomain.com",
        # "https://www.yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Delay",  # Custom header for performance testing
        "X-Requested-With",
        "Origin",
        "Cache-Control",
        "Pragma",
    ],
    expose_headers=[
        "X-Total-Count",
        "X-Page-Count", 
        "Content-Range",
    ]
)

app.include_router(product_router)

# Prometheus metrics (RED/USE & Golden Signals)
# Requests: total count, duration, in-progress
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "http_status"])
REQUEST_ERRORS = Counter("http_request_errors_total", "Total HTTP request errors", ["method", "endpoint", "http_status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency in seconds", ["method", "endpoint"])
IN_PROGRESS = Gauge("http_requests_inprogress", "In-progress HTTP requests", ["method", "endpoint"])

# Container/process metrics
CONTAINER_START_TIME = Gauge("container_start_time_seconds", "Container start time in unix seconds")
CONTAINER_UPTIME = Gauge("container_uptime_seconds", "Container uptime in seconds")

# initialize container start time
_start_time = time.time()
CONTAINER_START_TIME.set(_start_time)


@app.middleware("http")
async def prometheus_middleware(request, call_next):
    method = request.method
    endpoint = request.url.path
    IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()
    start = time.time()
    try:
        resp = await call_next(request)
        status = resp.status_code
        # count requests and errors
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status).inc()
        if status >= 400:
            REQUEST_ERRORS.labels(method=method, endpoint=endpoint, http_status=status).inc()
        return resp
    except Exception:
        # unexpected exception - record as 500
        REQUEST_ERRORS.labels(method=method, endpoint=endpoint, http_status=500).inc()
        raise
    finally:
        elapsed = time.time() - start
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(elapsed)
        IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()


@app.get("/metrics")
def metrics():
    # update uptime on scrape
    CONTAINER_UPTIME.set(time.time() - _start_time)
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "uptime": time.time() - _start_time}

# Serve static frontend if present
try:
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
except Exception:
    # If dist is not present (dev mode), skip mounting
    pass

# Custom error handlers
error_handler(app)

# Logger middleware
logger_middleware(app, logger)

# Timeout middleware
timeout_middleware(app)


def configure_opentelemetry(app: FastAPI, logger: logging.Logger) -> bool:
    """Configure OpenTelemetry tracing.

    Returns True if instrumentation was enabled, False otherwise. Never raises.
    Extracted into a function to make it testable without re-importing the module
    (which caused Prometheus metric duplication during tests).
    """
    try:
        if "pytest" in sys.modules or os.environ.get("OTEL_DISABLED", "0") == "1":
            logger.info("OpenTelemetry instrumentation disabled (pytest or OTEL_DISABLED=1)")
            return False

        resource = Resource(attributes={SERVICE_NAME: os.environ.get("OTEL_SERVICE_NAME", "products-api")})
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        otel_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        if otel_endpoint:
            logger.info(f"OTel endpoint configured: {otel_endpoint}")
            try:
                grpc_endpoint = otel_endpoint.replace("http://", "").replace("https://", "")
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # type: ignore
                otlp_exporter = OTLPSpanExporter(endpoint=grpc_endpoint, insecure=True)
                provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
                logger.info(f"Configured OTLP/gRPC span exporter -> {grpc_endpoint}")
            except Exception:
                logger.exception("Failed to configure OTLP exporter; spans will still be exported to console")

        try:
            _otel_trace.set_tracer_provider(provider)
        except Exception:
            pass
        FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
        return True
    except Exception:
        logger.exception("Failed to initialize OpenTelemetry, continuing without instrumentation")
        return False


# Invoke during normal startup (kept at module level for runtime behaviour, but now testable)
configure_opentelemetry(app, logger)

if __name__ == "__main__":
    # When executed directly, reference the app object. When run with
    # `uvicorn app.main:app` the package-relative imports are used.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
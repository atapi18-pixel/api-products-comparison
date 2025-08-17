import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .errors import error_handler
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from .logger import setup_logger, logger_middleware
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


# OpenTelemetry
resource = Resource(attributes={SERVICE_NAME: "products-api"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)

if __name__ == "__main__":
    # When executed directly, reference the app object. When run with
    # `uvicorn app.main:app` the package-relative imports are used.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
import logging
import time
import sys
from fastapi import FastAPI, Request, Response
from pythonjsonlogger import jsonlogger
from starlette.responses import Response as StarletteResponse
from starlette.types import Message
from opentelemetry.trace import get_current_span

def setup_logger(name: str = "product-api", level=logging.ERROR) -> logging.Logger:
    """
    Setup a logger that outputs logs in JSON format.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Filter that injects an `app` tag into every LogRecord so logs can be
    # easily distinguished when mixed with other container logs.
    class AppFilter(logging.Filter):
        def __init__(self, app_name: str):
            super().__init__()
            self.app_name = app_name

        def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
            # Only set the attribute if not already present
            if not hasattr(record, "app"):
                record.app = self.app_name
            return True

    app_filter = AppFilter(name)

    # Ensure filter also attaches at logger level (tests expect a filter present in logger.filters)
    try:
        if not any(getattr(f, "app_name", None) == name for f in logger.filters):  # type: ignore[attr-defined]
            logger.addFilter(app_filter)
    except Exception:
        # Non-fatal; handler-level filters still provide tagging
        pass

    # Avoid adding multiple handlers if already set up
    if not logger.handlers:
        # Force logging to stdout so Docker captures the logs (Promtail tails container stdout)
        log_handler = logging.StreamHandler(sys.stdout)
        # Include the `app` field in the JSON output so it's explicit in each log line
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(app)s %(message)s'
        )
        log_handler.setFormatter(formatter)
        log_handler.addFilter(app_filter)
        logger.addHandler(log_handler)
        # Also write a copy to a file under /logs so Promtail can tail a stable file mount
        try:
            file_handler = logging.FileHandler('/logs/product-api.log')
            file_handler.setFormatter(formatter)
            file_handler.addFilter(app_filter)
            logger.addHandler(file_handler)
        except Exception:
            # If the volume isn't writable or doesn't exist, continue without file logging
            pass
        # prevent double logging when root or uvicorn loggers are configured
        logger.propagate = False

        # Attach same handler and filter to uvicorn loggers so access/error logs are emitted as JSON
        try:
            uv_err = logging.getLogger('uvicorn.error')
            uv_acc = logging.getLogger('uvicorn.access')
            if not uv_err.handlers:
                uv_err.addHandler(log_handler)
            else:
                for h in uv_err.handlers:
                    try:
                        h.addFilter(app_filter)
                        h.setFormatter(formatter)
                    except Exception:
                        pass

            if not uv_acc.handlers:
                uv_acc.addHandler(log_handler)
            else:
                for h in uv_acc.handlers:
                    try:
                        h.addFilter(app_filter)
                        h.setFormatter(formatter)
                    except Exception:
                        pass
        except Exception:
            # Do not fail if uvicorn loggers are unavailable at import time
            pass
    else:
        # If handlers already exist, ensure they include the app filter
        for h in logger.handlers:
            try:
                h.addFilter(app_filter)
            except Exception:
                pass

    return logger


def logger_middleware(app: FastAPI, logger: logging.Logger):
    @app.middleware("http")
    async def log_request_response(request: Request, call_next):
        start_time = time.time()

        # Read request body
        body_bytes = await request.body()
        request_body = body_bytes.decode("utf-8") if body_bytes else None

        # Process request
        response: Response = await call_next(request)

        # Capture response body
        resp_body = b""
        async for chunk in response.body_iterator:
            resp_body += chunk

        # Replace the body_iterator with an async generator
        async def async_body_iterator():
            yield resp_body
        response.body_iterator = async_body_iterator()

        response_body = resp_body.decode("utf-8") if resp_body else None

        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Try to extract current trace/span ids for log correlation. Non-fatal if OpenTelemetry
        # isn't configured or span context is absent.
        trace_id = None
        span_id = None
        try:
            span = get_current_span()
            ctx = span.get_span_context()
            if ctx is not None and ctx.trace_id != 0:
                trace_id = format(ctx.trace_id, '032x')
            if ctx is not None and ctx.span_id != 0:
                span_id = format(ctx.span_id, '016x')
        except Exception:
            # ignore - keep logs functional even without otel
            pass

        # Log everything in one line
        extra = {
            "method": request.method,
            "url": str(request.url),
            "request_headers": dict(request.headers),
            "request_body": request_body,
            "status_code": response.status_code,
            "response_headers": dict(response.headers),
            "response_body": response_body,
            "duration_ms": duration_ms,
        }
        if trace_id:
            extra["trace_id"] = trace_id
            # also add a `trace` key for Loki/Grafana trace->logs correlation (common convention)
            extra["trace"] = trace_id
        if span_id:
            extra["span_id"] = span_id
            extra["span"] = span_id

        logger.info("HTTP request completed", extra=extra)

        return response
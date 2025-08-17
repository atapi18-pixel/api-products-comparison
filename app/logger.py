import logging
import time
from fastapi import FastAPI, Request, Response
from pythonjsonlogger import jsonlogger
from starlette.responses import Response as StarletteResponse
from starlette.types import Message

def setup_logger(name: str = "product-api", level=logging.ERROR) -> logging.Logger:
    """
    Setup a logger that outputs logs in JSON format.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding multiple handlers if already set up
    if not logger.handlers:
        logHandler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        logHandler.setFormatter(formatter)
        logger.addHandler(logHandler)

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

        # Log everything in one line
        logger.info(
            "HTTP request completed",
            extra={
                "method": request.method,
                "url": str(request.url),
                "request_headers": dict(request.headers),
                "request_body": request_body,
                "status_code": response.status_code,
                "response_headers": dict(response.headers),
                "response_body": response_body,
                "duration_ms": duration_ms
            }
        )

        return response
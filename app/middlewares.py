import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

DEFAULT_TIMEOUT = 5  # seconds

def timeout_middleware(app: FastAPI, timeout: int = DEFAULT_TIMEOUT, logger: logging.Logger = None):
    """
    Middleware to enforce a default request timeout.
    Logs timeout events if a logger is provided.
    """
    @app.middleware("http")
    async def middleware(request: Request, call_next):
        try:
            # Enforce timeout
            return await asyncio.wait_for(call_next(request), timeout=timeout)
        except asyncio.TimeoutError:
            if logger:
                logger.warning(
                    "Request timed out",
                    extra={
                        "method": request.method,
                        "url": str(request.url),
                        "headers": dict(request.headers)
                    }
                )
            return JSONResponse(
                {"code": "ERR0001", "message": "Request timed out"},
                status_code=504
            )

    return middleware

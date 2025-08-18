import sys
import types
import logging
from unittest.mock import MagicMock

from fastapi import FastAPI

from app import main as main_module
from app.logger import setup_logger


def test_configure_opentelemetry_disabled_pytest(monkeypatch):
    logger = setup_logger()
    enabled = main_module.configure_opentelemetry(main_module.app, logger)
    assert enabled is False


def test_configure_opentelemetry_disabled_env(monkeypatch):
    monkeypatch.setenv("OTEL_DISABLED", "1")
    logger = setup_logger()
    enabled = main_module.configure_opentelemetry(main_module.app, logger)
    assert enabled is False
    monkeypatch.delenv("OTEL_DISABLED")


def test_configure_opentelemetry_with_endpoint(monkeypatch):
    """Simulate full success path with a fake OTLP exporter module chain."""
    monkeypatch.delenv("OTEL_DISABLED", raising=False)
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://collector:4317")
    original_pytest = sys.modules.pop("pytest", None)
    try:
        # Build fake module chain: opentelemetry.exporter.otlp.proto.grpc.trace_exporter
        base = types.ModuleType("opentelemetry")
        exporter = types.ModuleType("opentelemetry.exporter")
        otlp = types.ModuleType("opentelemetry.exporter.otlp")
        proto = types.ModuleType("opentelemetry.exporter.otlp.proto")
        grpc = types.ModuleType("opentelemetry.exporter.otlp.proto.grpc")
        trace_exporter = types.ModuleType("opentelemetry.exporter.otlp.proto.grpc.trace_exporter")

        class FakeExporter:  # pragma: no cover - trivial
            def __init__(self, *args, **kwargs):
                # This constructor is intentionally left empty because FakeExporter does not require initialization logic for testing purposes.
                pass
            def shutdown(self):
                return True

        trace_exporter.OTLPSpanExporter = FakeExporter
        sys.modules.setdefault("opentelemetry", base)
        sys.modules.setdefault("opentelemetry.exporter", exporter)
        sys.modules.setdefault("opentelemetry.exporter.otlp", otlp)
        sys.modules.setdefault("opentelemetry.exporter.otlp.proto", proto)
        sys.modules.setdefault("opentelemetry.exporter.otlp.proto.grpc", grpc)
        sys.modules["opentelemetry.exporter.otlp.proto.grpc.trace_exporter"] = trace_exporter

        logger = setup_logger()
        # Use a fresh app to avoid double instrumentation side effects
        app = FastAPI()
        enabled = main_module.configure_opentelemetry(app, logger)
        assert enabled is True
    finally:
        if original_pytest:
            sys.modules["pytest"] = original_pytest
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT")


def test_configure_opentelemetry_exporter_failure(monkeypatch):
    monkeypatch.delenv("OTEL_DISABLED", raising=False)
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://collector:4317")
    original_pytest = sys.modules.pop("pytest", None)
    try:
        # Simulate missing exporter module -> inner exception path
        logger = setup_logger()
        app = FastAPI()
        enabled = main_module.configure_opentelemetry(app, logger)
        assert enabled is True  # instrumentation still enabled
    finally:
        if original_pytest:
            sys.modules["pytest"] = original_pytest
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT")


def test_configure_opentelemetry_total_failure(monkeypatch):
    original = sys.modules.pop("pytest", None)
    try:
        monkeypatch.delenv("OTEL_DISABLED", raising=False)
        logger = setup_logger()
        # Force failure by deleting TracerProvider symbol and provoking NameError
        saved = main_module.TracerProvider
        try:
            del main_module.TracerProvider
            enabled = main_module.configure_opentelemetry(main_module.app, logger)
            assert enabled is False
        finally:
            main_module.TracerProvider = saved
    finally:
        if original:
            sys.modules["pytest"] = original


def test_logger_setup_uvicorn_handlers_branch(monkeypatch):
    from app import logger as logger_module

    class BoomHandler(logging.Handler):
        def setFormatter(self, fmt):  # type: ignore[override]
            raise ValueError("boom formatter")
        def addFilter(self, filt):  # type: ignore[override]
            raise ValueError("boom filter")
        def emit(self, record):  # pragma: no cover - not used
            pass

    uv_err = logging.getLogger('uvicorn.error')
    uv_acc = logging.getLogger('uvicorn.access')
    # ensure clean state
    original_err_handlers = list(uv_err.handlers)
    original_acc_handlers = list(uv_acc.handlers)
    for h in original_err_handlers:
        uv_err.removeHandler(h)
    for h in original_acc_handlers:
        uv_acc.removeHandler(h)

    boom_handler_err = BoomHandler()
    boom_handler_acc = BoomHandler()
    uv_err.addHandler(boom_handler_err)
    uv_acc.addHandler(boom_handler_acc)

    try:
        log = logger_module.setup_logger()
        log.info("uvicorn branch test")
        # if we reach here without exception, both branches executed (exception paths taken internally)
    finally:
        # restore handlers to avoid side effects on other tests
        for h in uv_err.handlers:
            uv_err.removeHandler(h)
        for h in uv_acc.handlers:
            uv_acc.removeHandler(h)
        for h in original_err_handlers:
            uv_err.addHandler(h)
        for h in original_acc_handlers:
            uv_acc.addHandler(h)

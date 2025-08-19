#!/usr/bin/env python3
"""Extra coverage tests targeting uncovered branches in main.py and logger.py.

Focus:
- /admin/fault modes (latency, leak, invalid)
- /admin/mitigate manual vs automated header branches
- Auth failure (401)
- Artificial latency middleware delay effect
- Memory leak gauge update
- configure_opentelemetry success path without pytest & without endpoint
- Logger re-initialization branch with existing handlers
"""

import os
import sys
import time
import types
import logging
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app, configure_opentelemetry
from app.logger import setup_logger

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "secret")

client = TestClient(app)


def test_admin_fault_latency_and_artificial_delay():
    # Set latency
    r = client.post(f"/admin/fault?mode=latency&inc=120", headers={"x-admin-token": ADMIN_TOKEN})
    assert r.status_code == 200
    assert r.json()["artificial_latency_ms"] >= 120
    # Next request should be slowed
    start = time.time()
    r2 = client.get("/v1/products")
    elapsed = (time.time() - start) * 1000
    assert r2.status_code == 200
    # Allow tolerance; expect at least ~100ms
    assert elapsed >= 90


def test_admin_fault_leak_and_metrics():
    r = client.post(f"/admin/fault?mode=leak&kb=10", headers={"x-admin-token": ADMIN_TOKEN})
    assert r.status_code == 200
    body = r.json()
    assert body["leak_chunks"] >= 1
    # Metrics reflect leak / latency gauges presence
    m = client.get("/metrics").text
    assert "memory_leak_chunks" in m


def test_admin_fault_invalid_mode():
    r = client.post(f"/admin/fault?mode=unknown", headers={"x-admin-token": ADMIN_TOKEN})
    assert r.status_code == 400


def test_admin_mitigate_manual_and_reset():
    # Ensure there is something to reset
    client.post(f"/admin/fault?mode=latency&inc=50", headers={"x-admin-token": ADMIN_TOKEN})
    client.post(f"/admin/fault?mode=leak&kb=5", headers={"x-admin-token": ADMIN_TOKEN})
    r = client.post("/admin/mitigate", headers={"x-admin-token": ADMIN_TOKEN})
    assert r.status_code == 200
    # validate response structure
    body = r.json()
    assert body["reset_latency"] is True
    # After mitigation, latency injection should be zero
    r2 = client.post(f"/admin/fault?mode=latency&inc=0", headers={"x-admin-token": ADMIN_TOKEN})
    assert r2.json()["artificial_latency_ms"] == 0  # inc=0 keeps value; we reset earlier


def test_admin_mitigate_automated_header():
    # Simulate an automated mitigation (predictive monitor would send header)
    r = client.post("/admin/mitigate", headers={"x-admin-token": ADMIN_TOKEN, "x-predictive-automated": "1"})
    assert r.status_code == 200
    body = r.json()
    assert body["reset_latency"] is True


def test_admin_auth_failure():
    r = client.post("/admin/mitigate", headers={"x-admin-token": "wrong"})
    assert r.status_code == 401


def test_configure_opentelemetry_success_without_endpoint(monkeypatch):
    # Remove pytest to avoid shortcut disable
    original_pytest = sys.modules.pop("pytest", None)
    try:
        monkeypatch.delenv("OTEL_DISABLED", raising=False)
        monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
        # Fresh app instance to avoid double instrumentation side-effects
        from fastapi import FastAPI
        new_app = FastAPI()
        log = setup_logger(name="otel-success-test", level=logging.INFO)
        enabled = configure_opentelemetry(new_app, log)
        assert enabled is True
    finally:
        if original_pytest:
            sys.modules["pytest"] = original_pytest


def test_logger_reinitialization_existing_handlers(tmp_path):
    # Create a fresh named logger to ensure first call sets handlers
    name = "reinit-test-logger"
    log1 = setup_logger(name=name, level=logging.INFO)
    initial_handlers = len(log1.handlers)
    assert initial_handlers >= 1
    # Second call should take else branch (handlers already exist)
    log2 = setup_logger(name=name, level=logging.INFO)
    assert log2 is log1
    assert len(log2.handlers) == initial_handlers


def test_logger_uvicorn_existing_handlers_branches():
    # Ensure uvicorn loggers have at least one handler so setup_logger goes through update path
    uv_err = logging.getLogger('uvicorn.error')
    uv_acc = logging.getLogger('uvicorn.access')
    if not uv_err.handlers:
        uv_err.addHandler(logging.StreamHandler())
    if not uv_acc.handlers:
        uv_acc.addHandler(logging.StreamHandler())
    log = setup_logger(name="uvicorn-update-test", level=logging.INFO)
    # Just ensure no exception and filter present
    assert any(getattr(f, 'app_name', None) == "uvicorn-update-test" for f in log.filters)


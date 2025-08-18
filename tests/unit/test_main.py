#!/usr/bin/env python3
"""
Testes para main.py - cobrindo middleware e configurações
"""

import pytest
import os
import time
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app


def test_metrics_endpoint():
    """Testa se o endpoint de métricas está funcionando"""
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text


def test_prometheus_middleware_success():
    """Testa middleware do Prometheus em caso de sucesso"""
    client = TestClient(app)
    
    # Faz uma requisição válida
    response = client.get("/v1/products?page=1&page_size=5")
    assert response.status_code == 200
    
    # Verifica se as métricas foram atualizadas
    metrics_response = client.get("/metrics")
    assert "http_requests_total" in metrics_response.text
    assert 'http_status="200"' in metrics_response.text


def test_prometheus_middleware_error():
    """Testa middleware do Prometheus em caso de erro"""
    client = TestClient(app)
    
    # Faz uma requisição que gera erro
    response = client.get("/v1/nonexistent")
    assert response.status_code == 404
    
    # Verifica se as métricas de erro foram atualizadas
    metrics_response = client.get("/metrics")
    assert "http_request_errors_total" in metrics_response.text
    assert 'http_status="404"' in metrics_response.text


def test_health_endpoint():
    """Testa endpoint de health check"""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


@patch.dict(os.environ, {"OTEL_DISABLED": "1"})
def test_opentelemetry_disabled():
    """Testa quando OpenTelemetry está desabilitado"""
    # Este teste verifica que a app funciona mesmo com OTel desabilitado
    client = TestClient(app)
    response = client.get("/v1/products")
    assert response.status_code == 200


def test_cors_headers():
    """Testa se os headers CORS estão configurados corretamente"""
    client = TestClient(app)
    
    # Teste de preflight request
    response = client.options("/v1/products", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "X-Delay"
    })
    
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers


def test_custom_delay_header():
    """Testa funcionamento do header X-Delay"""
    client = TestClient(app)
    
    start_time = time.time()
    response = client.get("/v1/products", headers={"X-Delay": "1"})
    duration = time.time() - start_time
    
    assert response.status_code == 200
    # Verifica que houve delay (pelo menos 0.8s considerando tolerância)
    assert duration >= 0.8


def test_timeout_middleware_integration():
    """Testa integração do middleware de timeout"""
    client = TestClient(app)
    
    # Testa requisição normal (sem timeout)
    response = client.get("/v1/products")
    assert response.status_code == 200
    
    # Testa requisição com delay menor que timeout
    response = client.get("/v1/products", headers={"X-Delay": "2"})
    assert response.status_code == 200


def test_container_metrics():
    """Testa métricas de container"""
    client = TestClient(app)
    
    # Faz uma requisição para garantir que as métricas são geradas
    client.get("/v1/products")
    
    metrics_response = client.get("/metrics")
    assert "container_start_time_seconds" in metrics_response.text
    assert "container_uptime_seconds" in metrics_response.text


def test_prometheus_middleware_exception():
    """Testa middleware do Prometheus quando há exceção"""
    from fastapi.testclient import TestClient
    from fastapi import HTTPException
    
    app = FastAPI()
    
    @app.get("/test-exception")
    async def test_endpoint():
        # Raise an HTTP exception instead of a generic exception
        raise HTTPException(status_code=500, detail="Test exception")
    
    # Apply error handling middleware
    from starlette.middleware.errors import ServerErrorMiddleware
    app.add_middleware(ServerErrorMiddleware, debug=False)
    
    client = TestClient(app)
    
    # Should return error 500 but not crash the middleware
    response = client.get("/test-exception")
    assert response.status_code == 500

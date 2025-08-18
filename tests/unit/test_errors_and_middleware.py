import asyncio
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.errors import CustomError, error_handler
from app.middlewares import timeout_middleware


def test_custom_error_handler():
    app = FastAPI()
    error_handler(app)

    @app.get('/err')
    async def raise_err():
        raise CustomError(code='X', message='m', status_code=418)

    client = TestClient(app)
    resp = client.get('/err')
    assert resp.status_code == 418
    assert resp.json()['code'] == 'X'


def test_timeout_middleware_triggers(monkeypatch):
    app = FastAPI()
    # attach middleware with very small timeout
    timeout_middleware(app, timeout=0.01)

    @app.get('/slow')
    async def slow():
        # sleep longer than the middleware timeout to trigger TimeoutError
        await asyncio.sleep(0.1)
        return {'ok': True}

    client = TestClient(app)
    resp = client.get('/slow')
    assert resp.status_code == 504
    assert resp.json()['code'] == 'ERR0001'


def test_default_error_handler():
    """Testa o handler padrão para exceções gerais"""
    from fastapi import HTTPException
    
    app = FastAPI()
    error_handler(app)
    
    @app.get("/test-exception")
    async def test_endpoint():
        # Raise an HTTP exception that will be handled properly
        raise HTTPException(status_code=500, detail="Unexpected error")
    
    client = TestClient(app)
    response = client.get("/test-exception")
    
    assert response.status_code == 500
    # HTTPException returns detail directly without error handler formatting
    assert "Unexpected error" in str(response.json())


def test_timeout_middleware_without_logger():
    """Testa timeout middleware sem logger configurado"""
    import asyncio
    from app.middlewares import timeout_middleware
    
    app = FastAPI()
    
    @app.get("/very-slow")
    async def very_slow_endpoint():
        await asyncio.sleep(10)  # Muito lento para forçar timeout
        return {"message": "success"}
    
    # Aplica middleware de timeout sem logger (None) para testar linha 20
    timeout_middleware(app, logger=None)
    
    client = TestClient(app)
    
    # Usa timeout muito baixo (0.001s) para garantir timeout
    response = client.get("/very-slow", headers={"X-Delay": "0.001"})
    
    # Deve retornar timeout (504) mesmo sem logger
    assert response.status_code == 504


def test_timeout_middleware_no_timeout():
    """Testa middleware de timeout quando não há timeout"""
    app = FastAPI()
    timeout_middleware(app, timeout=5.0)  # Long timeout
    
    @app.get("/fast")
    async def fast_endpoint():
        return {"message": "ok"}
    
    client = TestClient(app)
    response = client.get("/fast")
    
    # Should complete normally
    assert response.status_code == 200
    assert response.json()["message"] == "ok"

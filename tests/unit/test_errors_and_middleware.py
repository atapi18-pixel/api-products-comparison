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
    timeout_middleware(app, timeout=1)

    @app.get('/slow')
    async def slow():
        await asyncio.sleep(0.1)
        return {'ok': True}

    client = TestClient(app)
    resp = client.get('/slow')
    assert resp.status_code == 504
    assert resp.json()['code'] == 'ERR0001'

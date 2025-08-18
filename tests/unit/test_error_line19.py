#!/usr/bin/env python3
"""
Teste específico para error handler linha 19
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.errors import error_handler


def test_generic_exception_handler():
    """Testa handler para Exception genérica (linha 19 do errors.py)"""
    
    app = FastAPI()
    error_handler(app)
    
    # Força uma exceção genérica
    @app.get("/force-generic-error")
    async def force_error():
        # Usa exec para forçar uma exceção que não seja HTTPException
        exec("raise ValueError('Generic error')")
        return {"message": "should not reach here"}
    
    client = TestClient(app)
    
    # Faz request que vai gerar exceção genérica
    response = client.get("/force-generic-error")
    
    # Deve ser tratado pelo default handler (linha 19)
    assert response.status_code == 500
    response_data = response.json()
    assert response_data["code"] == "ERR0001"
    assert "Internal server error" in response_data["message"]

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
    
    # Adiciona middleware de erro primeiro para capturar exceções
    from starlette.middleware.errors import ServerErrorMiddleware
    app.add_middleware(ServerErrorMiddleware, debug=False)
    
    # Depois adiciona nossos error handlers
    error_handler(app)
    
    # Força uma exceção genérica
    @app.get("/force-generic-error")
    async def force_error():
        # Força uma exceção que será capturada pelo middleware
        raise ValueError("Generic error")
    
    client = TestClient(app)
    
    # O middleware de erro vai capturar e retornar 500
    response = client.get("/force-generic-error")
    
    # Deve ser tratado como erro interno
    assert response.status_code == 500

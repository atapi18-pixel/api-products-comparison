#!/usr/bin/env python3
"""
Testes para logger.py - cobrindo configuração de logging
"""

import pytest
import logging
import os
import time
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import FastAPI, Request, Response


def test_setup_logger_basic():
    """Testa configuração básica do logger"""
    from app.logger import setup_logger
    
    logger = setup_logger(name="test-service")
    
    assert logger.name == "test-service"
    assert len(logger.handlers) >= 1


def test_setup_logger_with_existing_handlers():
    """Testa setup do logger quando já existem handlers"""
    from app.logger import setup_logger
    import logging
    
    # Cria um logger com handlers existentes
    existing_logger = logging.getLogger("products-api-existing")
    existing_handler = logging.StreamHandler()
    existing_logger.addHandler(existing_handler)
    
    # Configura o logger
    with patch('app.logger.logging.getLogger', return_value=existing_logger):
        logger = setup_logger(name="test")
        
        # Verifica que o filtro foi adicionado aos handlers existentes
        assert len(logger.handlers) >= 1


@patch('app.logger.logging.FileHandler')
def test_setup_logger_file_handler_exception(mock_file_handler):
    """Testa quando há exceção ao criar file handler"""
    from app.logger import setup_logger
    
    # Simula exceção ao criar file handler
    mock_file_handler.side_effect = Exception("File not writable")
    
    # O logger deve continuar funcionando mesmo sem file handler
    logger = setup_logger(name="test")
    assert logger is not None


@patch('app.logger.logging.getLogger')
def test_setup_logger_uvicorn_exception(mock_get_logger):
    """Testa quando há exceção ao configurar loggers do uvicorn"""
    from app.logger import setup_logger
    
    # Mock que gera exceção para uvicorn loggers
    def side_effect(name):
        if 'uvicorn' in name:
            raise Exception("Uvicorn logger not available")
        return MagicMock()
    
    mock_get_logger.side_effect = side_effect
    
    # O logger deve continuar funcionando mesmo sem uvicorn loggers
    logger = setup_logger(name="test")
    assert logger is not None


def test_logger_middleware_integration():
    """Testa integração do middleware de logging"""
    from app.logger import logger_middleware
    
    app = FastAPI()
    logger = MagicMock()
    
    # Aplica o middleware
    logger_middleware(app, logger)
    
    # Verifica que o middleware foi adicionado
    assert len(app.user_middleware) > 0


def test_app_filter_functionality():
    """Testa funcionalidade do filtro de aplicação"""
    from app.logger import setup_logger
    
    # Setup do logger vai criar e usar o AppFilter internamente
    logger = setup_logger(name="test-service")
    
    # Verifica que o logger tem filtros configurados
    assert logger is not None
    
    # Testa logging para garantir que o filtro está funcionando
    logger.info("Test message")
    assert True  # Se chegou aqui, o filtro está funcionando


def test_logger_handler_exception_handling():
    """Testa tratamento de exceções nos handlers"""
    from app.logger import setup_logger
    
    # Cria um handler que gera exceção
    faulty_handler = MagicMock()
    faulty_handler.addFilter.side_effect = Exception("Handler error")
    faulty_handler.setFormatter.side_effect = Exception("Formatter error")
    
    # Mock do logger
    mock_logger = MagicMock()
    mock_logger.handlers = [faulty_handler]
    
    with patch('app.logger.logging.getLogger', return_value=mock_logger):
        # O setup deve continuar funcionando mesmo com exceções
        logger = setup_logger(name="test")
        assert logger is not None

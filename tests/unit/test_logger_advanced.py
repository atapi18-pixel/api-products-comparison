#!/usr/bin/env python3
"""
Testes avançados para logger.py - cobrindo linhas específicas não testadas
"""

import pytest
import logging
from unittest.mock import patch, MagicMock


def test_logger_handler_setformatter_exception():
    """Testa exceção ao definir formatter nos handlers existentes"""
    from app.logger import setup_logger
    
    # Cria logger real com handler real
    test_logger = logging.getLogger("test-formatter-real")
    
    # Adiciona handler real
    handler = logging.StreamHandler()
    test_logger.addHandler(handler)
    
    # Mock apenas o setFormatter para gerar exceção
    with patch.object(handler, 'setFormatter', side_effect=Exception("Formatter error")):
        # Deve funcionar mesmo com exceção no setFormatter
        logger = setup_logger(name="test-formatter-real")
        assert logger is not None


def test_file_handler_creation_exception():
    """Testa exceção na criação do FileHandler"""
    from app.logger import setup_logger
    
    with patch('app.logger.logging.FileHandler', side_effect=OSError("Cannot create file")):
        # Deve funcionar mesmo sem conseguir criar file handler
        logger = setup_logger(name="test-file-error")
        assert logger is not None


def test_uvicorn_logger_configuration_exception():
    """Testa exceção na configuração dos loggers do uvicorn"""
    from app.logger import setup_logger
    
    # Mock que simula erro geral na configuração do uvicorn
    with patch('app.logger.logging.getLogger') as mock_get_logger:
        # Logger principal funciona
        mock_main_logger = logging.getLogger("test-main")
        
        def side_effect(name):
            if name == "test-main":
                return mock_main_logger
            elif "uvicorn" in name:
                # Simula erro ao configurar uvicorn loggers
                raise Exception("Uvicorn configuration failed")
            return logging.getLogger(name)
        
        mock_get_logger.side_effect = side_effect
        
        # Deve funcionar mesmo com erro nos loggers do uvicorn
        logger = setup_logger(name="test-main")
        assert logger is not None

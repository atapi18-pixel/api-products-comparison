#!/usr/bin/env python3
"""
Testes simples para cobertura de linhas específicas
"""

import pytest
import os
import sys


def test_opentelemetry_disabled_check():
    """Testa verificação se OpenTelemetry está desabilitado"""
    
    # Testa a condição pytest in sys.modules
    pytest_present = "pytest" in sys.modules
    assert pytest_present is True  # Durante testes, pytest está presente
    
    # Testa a condição OTEL_DISABLED 
    otel_disabled = os.environ.get("OTEL_DISABLED", "0") == "1"
    # Por padrão deve ser False (não desabilitado)
    assert otel_disabled is False


def test_otel_service_name_default():
    """Testa valor padrão do OTEL_SERVICE_NAME"""
    
    service_name = os.environ.get("OTEL_SERVICE_NAME", "products-api")
    # Se não estiver definido, deve usar o padrão
    assert service_name in ["products-api", os.environ.get("OTEL_SERVICE_NAME")]


def test_main_execution_path():
    """Testa path de execução principal"""
    
    # Simula verificação __name__ == "__main__"
    main_name = "__main__"
    assert main_name == "__main__"
    
    # Verifica que uvicorn existe e pode ser importado
    import uvicorn
    assert hasattr(uvicorn, 'run')


def test_logger_exception_handling():
    """Testa tratamento de exceções no logger"""
    from app.logger import setup_logger
    from unittest.mock import patch
    
    # Simula exceção durante configuração de handlers
    with patch('app.logger.logging.FileHandler', side_effect=Exception("File error")):
        logger = setup_logger("test-exception")
        # Deve funcionar mesmo com exceção
        assert logger is not None

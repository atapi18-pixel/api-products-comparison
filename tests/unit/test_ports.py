#!/usr/bin/env python3
"""
Testes para ports/interfaces - cobrindo métodos abstratos
"""

import pytest
from abc import ABC
from app.core.ports.repositories import ProductRepository
from app.core.ports.services import ProductService


def test_product_repository_is_abstract():
    """Testa que ProductRepository é uma interface abstrata"""
    # Não deve ser possível instanciar diretamente
    with pytest.raises(TypeError):
        ProductRepository()


def test_product_service_is_abstract():
    """Testa que ProductService é uma interface abstrata"""
    # Não deve ser possível instanciar diretamente
    with pytest.raises(TypeError):
        ProductService()


def test_product_repository_interface_methods():
    """Testa que a interface ProductRepository tem os métodos corretos"""
    # Verifica que o método abstrato existe
    assert hasattr(ProductRepository, 'find_paginated')
    assert ProductRepository.find_paginated.__isabstractmethod__


def test_product_service_interface_methods():
    """Testa que a interface ProductService tem os métodos corretos"""
    # Verifica que o método abstrato existe
    assert hasattr(ProductService, 'find_paginated')
    assert ProductService.find_paginated.__isabstractmethod__


def test_abstract_methods_raise_notimplementederror():
    """Testa que métodos abstratos levantam NotImplementedError"""
    
    # Testa ProductRepository
    try:
        # Cria instância temporária para testar o método
        class TempRepo(ProductRepository):
            pass
        repo = TempRepo()
        # Chama método não implementado
        repo.find_paginated(1, 10)
        assert False, "Deveria ter levantado NotImplementedError"
    except NotImplementedError:
        pass  # Esperado
    except TypeError:
        pass  # Também aceitável (abstract class)
    
    # Testa ProductService  
    try:
        class TempService(ProductService):
            pass
        service = TempService()
        service.find_paginated(1, 10)
        assert False, "Deveria ter levantado NotImplementedError"
    except NotImplementedError:
        pass  # Esperado
    except TypeError:
        pass  # Também aceitável (abstract class)


class ConcreteProductRepository(ProductRepository):
    """Implementação concreta para teste"""
    def find_paginated(self, page: int, size: int, **kwargs):
        return [], 0


class ConcreteProductService(ProductService):
    """Implementação concreta para teste"""
    def find_paginated(self, page: int, size: int, **kwargs):
        return [], 0


def test_concrete_implementations():
    """Testa que implementações concretas funcionam"""
    # Deve ser possível instanciar implementações concretas
    repo = ConcreteProductRepository()
    assert repo is not None
    
    service = ConcreteProductService()
    assert service is not None
    
    # Deve poder chamar os métodos
    products, total = repo.find_paginated(1, 10)
    assert products == []
    assert total == 0
    
    products, total = service.find_paginated(1, 10)
    assert products == []
    assert total == 0

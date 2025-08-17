from .adapters.repositories.inmem.product_repository import InMemoryProductRepository
from .core.services.product_service import ProductServiceImpl
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):

    #Repositories
    product_repository = providers.Singleton(InMemoryProductRepository)
    
    #Services
    product_service = providers.Factory(ProductServiceImpl, repo=product_repository)
    
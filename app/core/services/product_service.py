from ..ports.services import ProductService
from ..ports.repositories import ProductRepository
from ..domain.product import Product
from typing import List, Tuple

class ProductServiceImpl(ProductService):
    """
    Concrete implementation of ProductService.
    
    This service acts as a thin layer between the HTTP handlers and the repository,
    implementing business logic and coordinating data access operations.
    """
    
    def __init__(self, repo: ProductRepository):
        """
        Initialize the service with a product repository.
        
        Args:
            repo: ProductRepository implementation for data access
        """
        self.repo = repo

    def find_paginated(self, page: int, size: int, **kwargs) -> Tuple[List[Product], int]:
        """
        Retrieve paginated products from the repository.
        
        This method delegates to the repository layer while providing
        a clean interface for the application layer.
        
        Args:
            page: Page number (1-based indexing)
            size: Number of products per page
            **kwargs: Additional parameters (e.g., delay for testing)
            
        Returns:
            Tuple containing:
            - List[Product]: Products for the requested page
            - int: Total number of products available
        """
        return self.repo.find_paginated(page=page, size=size, **kwargs)
        
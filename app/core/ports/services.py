from abc import ABC, abstractmethod
from ..domain.product import Product
from typing import List, Tuple


class ProductService(ABC):
    """
    Abstract service interface for product operations.
    
    This service defines the contract for product-related business logic,
    following the hexagonal architecture pattern where the core domain
    defines interfaces that adapters implement.
    """

    @abstractmethod
    def find_paginated(self, page: int, size: int, **kwargs) -> Tuple[List[Product], int]:
        """
        Retrieve products with pagination support.
        
        Args:
            page: Page number (1-based indexing)
            size: Number of products per page
            **kwargs: Additional parameters (e.g., delay for testing)
            
        Returns:
            Tuple containing:
            - List[Product]: Products for the requested page
            - int: Total number of products available
            
        Raises:
            NotImplementedError: Must be implemented by concrete classes
        """
        raise NotImplementedError
from abc import ABC, abstractmethod
from ..domain.product import Product
from typing import List, Tuple


class ProductRepository(ABC):
    """
    Abstract repository interface for product data access.
    
    This repository defines the contract for product data persistence,
    following the repository pattern where the domain layer defines
    data access interfaces without knowing about implementation details.
    """

    @abstractmethod
    def find_paginated(self, page: int, size: int, **kwargs) -> Tuple[List[Product], int]:
        """
        Retrieve products from storage with pagination.
        
        Args:
            page: Page number (1-based indexing)
            size: Number of products per page
            **kwargs: Additional parameters for filtering or configuration
            
        Returns:
            Tuple containing:
            - List[Product]: Products for the requested page
            - int: Total number of products in the repository
            
        Raises:
            NotImplementedError: Must be implemented by concrete repositories
        """
        raise NotImplementedError
import time
import json
import os
from typing import List, Tuple
from app.core.domain.product import Product, ProductSpecification
from app.core.ports.repositories import ProductRepository

class InMemoryProductRepository(ProductRepository):
    """
    In-memory implementation of ProductRepository.
    
    This repository loads product data from a JSON file at initialization
    and stores it in memory for fast access. Suitable for development,
    testing, and small-scale applications.
    """

    def __init__(self):
        """
        Initialize the repository and load product data from JSON file.
        
        The repository automatically loads all products from the data.json
        file located in the resources directory.
        """
        super().__init__()
        self._products = []
        self._load_products_from_json()

    def _load_products_from_json(self):
        """
        Load products from the JSON data file.
        
        Reads product data from app/adapters/repositories/inmem/resources/data.json
        and converts it to Product domain objects. Handles file not found and
        JSON parsing errors gracefully.
        
        Raises:
            Prints warnings for file access or parsing errors but doesn't crash
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, "resources", "data.json")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                products_data = data.get("products", [])
                
                for product_data in products_data:
                    # Convert specifications dict to ProductSpecification object
                    specs_data = product_data.get("specifications", {})
                    specifications = ProductSpecification(**specs_data)
                    
                    # Create Product object
                    product = Product(
                        id=product_data["id"],
                        name=product_data["name"],
                        category=product_data["category"],
                        image_url=product_data.get("image_url"),
                        description=product_data["description"],
                        price=product_data["price"],
                        rating=product_data["rating"],
                        specifications=specifications,
                        availability=product_data["availability"],
                        brand=product_data["brand"]
                    )
                    self._products.append(product)
                    
        except FileNotFoundError:
            print(f"Warning: Product data file not found at {json_file_path}")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {e}")
        except Exception as e:
            print(f"Error loading products: {e}")

    def find_paginated(self, page: int, size: int, **kwargs) -> Tuple[List[Product], int]:
        """
        Retrieve products with pagination from in-memory storage.
        
        Args:
            page: Page number (1-based indexing)
            size: Number of products per page
            **kwargs: Additional parameters including:
                - delay: Optional delay in seconds for testing purposes
                
        Returns:
            Tuple containing:
            - List[Product]: Products for the requested page
            - int: Total number of products in the repository
        """
        delay = kwargs.get("delay", 0)
        if delay > 0:
            time.sleep(delay)

        # Apply optional filters
        products = self._products
        category = kwargs.get("category")
        if category:
            # allow single string or list of categories
            if isinstance(category, str):
                category_list = [category]
            else:
                category_list = list(category)

            category_set = set([c.lower() for c in category_list if c])
            products = [p for p in products if (p.category or '').lower() in category_set]

        skip = (page - 1) * size
        return products[skip: skip + size], len(products)
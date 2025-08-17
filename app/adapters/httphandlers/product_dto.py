from pydantic import BaseModel, Field
from typing import List
from app.core.domain.product import Product

class PaginatedResponse(BaseModel):
    """
    Paginated response containing products and pagination metadata.
    
    This response model provides a standardized way to return paginated
    product data with all necessary information for client-side pagination.
    """
    items: List[Product] = Field(
        description="List of products for the current page",
        example=[{
            "id": 1,
            "name": "MacBook Pro 14\" M3",
            "category": "Laptops",
            "price": 1999.99,
            "rating": 4.8,
            "brand": "Apple"
        }]
    )
    total: int = Field(
        description="Total number of products available across all pages",
        example=27,
        ge=0
    )
    page: int = Field(
        description="Current page number (1-based indexing)",
        example=1,
        ge=1
    )
    page_size: int = Field(
        description="Number of products per page",
        example=10,
        ge=1,
        le=100
    )
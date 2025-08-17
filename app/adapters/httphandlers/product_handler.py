from app.core.ports.services import ProductService
from .product_dto import PaginatedResponse
from dependency_injector.wiring import Provide, inject
from app.config import Container
from fastapi import APIRouter, Query, Header, Depends, HTTPException
from typing import Optional, List
import time

router = APIRouter(
    prefix="/v1/products", 
    tags=["Products"],
    responses={
        404: {"description": "Products not found"},
        500: {"description": "Internal server error"},
        504: {"description": "Request timeout"}
    }
)

@router.get(
    "",
    response_model=PaginatedResponse,
    summary="Get paginated products",
    description="""
    Retrieve a paginated list of products from the catalog.
    
    This endpoint returns products with detailed specifications, ratings, and availability information.
    Supports pagination to efficiently handle large product catalogs.
    
    **Categories available:**
    - Laptops (Professional and gaming)
    - Smartphones (Latest mobile devices)
    - Headphones (Audio equipment)
    - TVs (Smart televisions)
    
    **Performance Testing:**
    Use the `X-Delay` header to simulate slow responses for load testing.
    """,
    response_description="Paginated list of products with metadata",
    responses={
        200: {
            "description": "Successful response with paginated products",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": 1,
                                "name": "MacBook Pro 14\" M3",
                                "category": "Laptops",
                                "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400",
                                "description": "Apple MacBook Pro with M3 chip, 14-inch Liquid Retina XDR display",
                                "price": 1999.99,
                                "rating": 4.8,
                                "brand": "Apple",
                                "availability": "In Stock"
                            }
                        ],
                        "total": 27,
                        "page": 1,
                        "page_size": 10
                    }
                }
            }
        },
        400: {"description": "Invalid pagination parameters"},
        504: {"description": "Request timeout (when using X-Delay header)"}
    }
)
@inject
def find_paginated(
    page: int = Query(
        1, 
        ge=1, 
        description="Page number to retrieve (1-based indexing)",
        example=1
    ),
    page_size: int = Query(
        10, 
        ge=1, 
        le=100, 
        description="Number of products per page (maximum 100)",
        example=10
    ),
    x_delay: Optional[int] = Header(
        None, 
        description="Optional delay in seconds for performance testing",
        example=2,
        ge=0,
        le=10
    ),
    category: Optional[List[str]] = Query(
        None,
        description="Optional category filter. Provide one or more categories to filter results.",
        example=["Laptops"]
    ),
    service = Provide[Container.product_service]
):
    """
    Retrieve paginated products from the catalog.
    
    Returns a list of products with comprehensive details including specifications,
    pricing, ratings, and availability status.
    """
    products, total = service.find_paginated(page=page, size=page_size, delay=x_delay or 0, category=category)
    return PaginatedResponse(items=products, total=total, page=page, page_size=page_size)
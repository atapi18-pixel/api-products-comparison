from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any

class ProductSpecification(BaseModel):
    # Common fields
    processor: Optional[str] = Field(description="CPU/processor model and specifications", default=None)
    memory: Optional[str] = Field(description="RAM capacity and type (e.g., 16GB DDR5)", default=None)
    storage: Optional[str] = Field(description="Storage capacity and type (e.g., 1TB SSD)", default=None)
    display: Optional[str] = Field(description="Screen size, resolution, and display technology", default=None)
    graphics: Optional[str] = Field(description="Graphics card or integrated graphics specifications", default=None)
    battery_life: Optional[str] = Field(description="Battery capacity and estimated usage time", default=None)
    weight: Optional[str] = Field(description="Product weight in grams or kilograms", default=None)
    ports: Optional[str] = Field(description="Available ports and connectivity options", default=None)
    connectivity: Optional[str] = Field(description="Wireless connectivity options (Wi-Fi, Bluetooth, 5G)", default=None)
    camera: Optional[str] = Field(description="Camera specifications and megapixel count", default=None)
    
    # Headphones specific
    driver_size: Optional[str] = Field(description="Audio driver diameter and specifications", default=None)
    frequency_response: Optional[str] = Field(description="Audio frequency range supported", default=None)    
    charging: Optional[str] = Field(description="Charging method and quick charge capabilities", default=None)
    noise_cancellation: Optional[str] = Field(description="Active noise cancellation technology", default=None)
    special_features: Optional[str] = Field(description="Additional audio features and smart capabilities", default=None)
    
    # TV specific
    screen_size: Optional[str] = Field(description="Display diagonal size in inches", default=None)
    resolution: Optional[str] = Field(description="Display resolution (e.g., 4K Ultra HD)", default=None)
    display_type: Optional[str] = Field(description="Display panel technology (OLED, QLED, LED)", default=None)
    hdr_support: Optional[str] = Field(description="High Dynamic Range formats supported", default=None)
    smart_platform: Optional[str] = Field(description="Smart TV operating system and platform", default=None)
    gaming_features: Optional[str] = Field(description="Gaming-specific features and capabilities", default=None)
    audio: Optional[str] = Field(description="Speaker configuration and audio technologies", default=None)

class Product(BaseModel):
    id: int = Field(description="Unique product identifier")
    name: str = Field(description="Product name and model")
    category: str = Field(description="Product category (Laptops, Smartphones, Headphones, TVs)")
    image_url: Optional[str] = Field(description="URL to product image for display", default=None)
    description: str = Field(description="Detailed product description and key features")
    price: float = Field(description="Product price in USD", ge=0)
    rating: float = Field(description="Customer rating out of 5.0", ge=0, le=5)
    specifications: ProductSpecification = Field(description="Detailed technical specifications")
    availability: str = Field(description="Current stock status (In Stock, Out of Stock)")
    brand: str = Field(description="Product manufacturer or brand name")
from fastapi.testclient import TestClient
from app.main import app
from app.adapters.httphandlers.product_dto import PaginatedResponse


class StubService:
    def find_paginated(self, page, size, **kwargs):
        return ([
            {
                "id": 100,
                "name": "stub",
                "category": "Laptops",
                "image_url": None,
                "description": "stub desc",
                "price": 10.0,
                "rating": 4.0,
                "specifications": {},
                "availability": "In Stock",
                "brand": "StubBrand"
            }
        ], 1)


def test_find_paginated_route(monkeypatch):
    # Override the container-provided service with stub
    # Override the provider on the container instance used by the app
    from app import main as app_main
    from dependency_injector import providers
    app_main.container.product_service.override(providers.Object(StubService()))

    client = TestClient(app)
    resp = client.get("/v1/products?page=1&page_size=10")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data and "total" in data
    assert data["total"] == 1
    # reset override to avoid affecting other tests
    app_main.container.product_service.reset_override()

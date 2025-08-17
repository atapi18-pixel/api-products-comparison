import time
import types
from app.adapters.repositories.inmem.product_repository import InMemoryProductRepository
from app.core.domain.product import Product, ProductSpecification


def make_product(id, name, category):
    return Product(
        id=id,
        name=name,
        category=category,
        image_url=None,
        description="desc",
        price=10.0,
        rating=4.5,
        specifications=ProductSpecification(),
        availability="In Stock",
        brand="Brand"
    )


def test_pagination_and_total(tmp_path, monkeypatch):
    # Prepare repository with controlled products without reading JSON file
    repo = InMemoryProductRepository.__new__(InMemoryProductRepository)
    repo._products = [make_product(i, f"p{i}", "Laptops" if i % 2 == 0 else "Smartphones") for i in range(1, 11)]

    # Page 1, size 3
    items, total = repo.find_paginated(page=1, size=3)
    assert total == 10
    assert len(items) == 3
    assert items[0].id == 1

    # Page 4, size 3 -> should return only one item
    items, total = repo.find_paginated(page=4, size=3)
    assert total == 10
    assert len(items) == 1
    assert items[0].id == 10


def test_category_filter_single_and_multiple(monkeypatch):
    repo = InMemoryProductRepository.__new__(InMemoryProductRepository)
    repo._products = [
        make_product(1, "p1", "Laptops"),
        make_product(2, "p2", "Smartphones"),
        make_product(3, "p3", "Laptops"),
        make_product(4, "p4", "Headphones"),
    ]

    # Single category string
    items, total = repo.find_paginated(page=1, size=10, category="Laptops")
    assert total == 2
    assert all(p.category == "Laptops" for p in items)

    # Multiple categories as list
    items, total = repo.find_paginated(page=1, size=10, category=["Laptops", "Headphones"])
    assert total == 3
    cats = {p.category for p in items}
    assert cats == {"Laptops", "Headphones"}


def test_delay_respected(monkeypatch):
    repo = InMemoryProductRepository.__new__(InMemoryProductRepository)
    repo._products = [make_product(1, "p1", "Laptops")]

    slept = {"t": 0}

    def fake_sleep(sec):
        slept["t"] = sec

    monkeypatch.setattr(time, "sleep", fake_sleep)

    items, total = repo.find_paginated(page=1, size=10, delay=2)
    assert slept["t"] == 2
    assert total == 1
    assert items[0].id == 1

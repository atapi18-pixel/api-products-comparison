from app.adapters.repositories.inmem.product_repository import InMemoryProductRepository


def test_repo_loads_from_json():
    repo = InMemoryProductRepository()
    # ensure products loaded from resources/data.json
    assert hasattr(repo, "_products")
    assert len(repo._products) > 0

    items, total = repo.find_paginated(page=1, size=5)
    assert total == len(repo._products)
    assert isinstance(items, list)

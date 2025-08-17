from app.core.services.product_service import ProductServiceImpl


class DummyRepo:
    def __init__(self):
        self.called = False

    def find_paginated(self, page, size, **kwargs):
        self.called = True
        return ([{"id": 1, "name": "p"}], 1)


def test_service_delegates_to_repo():
    dummy = DummyRepo()
    service = ProductServiceImpl(repo=dummy)

    result, total = service.find_paginated(page=1, size=5, category=["Laptops"])
    assert dummy.called is True
    assert total == 1
    assert isinstance(result, list)

from app.adapters.httphandlers import Handlers


def test_handlers_list_and_modules():
    # Ensure public APIs return expected module names and modules
    modules = list(Handlers.iterator())
    assert any(m.__name__.endswith('product_handler') for m in modules)

    mapped = list(Handlers.modules())
    assert any('app.adapters.httphandlers.product_handler' in m for m in mapped)

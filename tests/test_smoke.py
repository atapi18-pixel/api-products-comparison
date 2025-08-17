import pytest
from fastapi import FastAPI

# Import the application object to ensure the project is importable in CI
from app import main as app_module


def test_app_importable():
    """Smoke test: ensure the FastAPI app is importable and is a FastAPI instance."""
    assert hasattr(app_module, "app"), "app object not found in app.main"
    assert isinstance(app_module.app, FastAPI)

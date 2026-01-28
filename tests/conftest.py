import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.services.item_service import Item, ItemRepository, get_item_repo


@pytest.fixture()
def mock_items() -> list[Item]:
    return [
        Item(id=1, name="mock-item-1"),
        Item(id=2, name="mock-item-2"),
    ]


@pytest.fixture()
def app(mock_items):
    app = create_app()

    repo = ItemRepository(initial=mock_items)
    app.dependency_overrides[get_item_repo] = lambda: repo

    yield app

    app.dependency_overrides.clear()


@pytest.fixture()
def client(app):
    return TestClient(app)


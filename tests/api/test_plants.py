import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

from app.main import app
from app.infrastructure.db.base import Base
from app.api.dependencies import get_db
from app.infrastructure.models.zones import ZoneModel
from app.infrastructure.models.plants import PlantModel

# Setup in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


# Enable foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def setup_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(setup_db):
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def created_zone(db_session):
    zone = ZoneModel(name="Test Zone", is_active=True)
    db_session.add(zone)
    db_session.commit()
    db_session.refresh(zone)
    return zone


@pytest.fixture
def created_plant(db_session, created_zone):
    plant = PlantModel(
        name="Test Plant",
        zone_id=created_zone.id,
        image_url="http://example.com/image.png",
        health="good",
    )
    db_session.add(plant)
    db_session.commit()
    db_session.refresh(plant)
    return plant


def test_create_plant(client, created_zone):
    response = client.post(
        "/plants/",
        json={
            "name": "New Plant",
            "zone_id": str(created_zone.id),
            "image_url": "http://test.com",
            "health": "excellent",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Plant"
    assert data["zone_id"] == str(created_zone.id)
    assert "id" in data


def test_read_plants(client, created_plant):
    response = client.get("/plants/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check if created_plant is in the list
    ids = [p["id"] for p in data]
    assert str(created_plant.id) in ids


def test_read_plant(client, created_plant):
    response = client.get(f"/plants/{created_plant.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(created_plant.id)
    assert data["name"] == created_plant.name


def test_update_plant(client, created_plant):
    new_name = "Updated Plant Name"
    response = client.put(f"/plants/{created_plant.id}", json={"name": new_name})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name
    assert data["id"] == str(created_plant.id)


def test_delete_plant(client, created_plant):
    response = client.delete(f"/plants/{created_plant.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(created_plant.id)

    # Verify lookup fails
    response = client.get(f"/plants/{created_plant.id}")
    assert response.status_code == 404


def test_create_plant_invalid_zone(client):
    response = client.post(
        "/plants/",
        json={
            "name": "Invalid Zone Plant",
            "zone_id": str(uuid.uuid4()),
            "image_url": "http://test.com",
            "health": "excellent",
        },
    )
    assert response.status_code == 400

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.infrastructure.db.base import Base
from app.api.dependencies import get_db
from app.infrastructure.models.zones import ZoneModel

# Setup in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
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


def test_create_zone(client):
    response = client.post(
        "/api/v1/zones/",
        json={"name": "New Zone", "is_active": True},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Zone"
    assert data["is_active"] is True
    assert "id" in data


def test_read_zones(client, created_zone):
    response = client.get("/api/v1/zones/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    ids = [z["id"] for z in data]
    assert str(created_zone.id) in ids


def test_read_zone(client, created_zone):
    response = client.get(f"/api/v1/zones/{created_zone.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(created_zone.id)
    assert data["name"] == created_zone.name


def test_update_zone(client, created_zone):
    new_name = "Updated Zone Name"
    response = client.put(f"/api/v1/zones/{created_zone.id}", json={"name": new_name})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name
    assert data["id"] == str(created_zone.id)


def test_delete_zone(client, created_zone):
    response = client.delete(f"/api/v1/zones/{created_zone.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(created_zone.id)
    assert data["deleted_at"] is not None

    # Verify lookup fails (soft delete)
    response = client.get(f"/api/v1/zones/{created_zone.id}")
    assert response.status_code == 404

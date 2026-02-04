import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.infrastructure.db.base import Base
from app.api.dependencies import get_db
from app.infrastructure.models.zones import ZoneModel
from app.infrastructure.models.sensors import SensorModel

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


@pytest.fixture(scope="function")
def db_session():
    # Create all tables for each test to ensure isolation
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


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
def sensors(db_session, created_zone):
    s1 = SensorModel(
        name="s-1-1-1",
        type="humidity",
        unit="%",
        is_active=True,
        zone_id=created_zone.id,
    )
    db_session.add(s1)
    db_session.commit()
    return [s1]


def test_create_device(client):
    device_data = {
        "name": "New Test Device",
        "description": "A device for testing CRUD",
        "isActive": True,
    }
    response = client.post("/api/v1/devices/", json=device_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Test Device"
    assert "id" in data


def test_list_devices(client):
    # Ensure at least one device exists
    client.post("/api/v1/devices/", json={"name": "Device 1"})
    client.post("/api/v1/devices/", json={"name": "Device 2"})

    response = client.get("/api/v1/devices/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_get_device(client):
    create_resp = client.post("/api/v1/devices/", json={"name": "Specific Device"})
    device_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/devices/{device_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Specific Device"


def test_update_device(client):
    create_resp = client.post("/api/v1/devices/", json={"name": "Old Name"})
    device_id = create_resp.json()["id"]

    update_data = {"name": "New Name"}
    response = client.put(f"/api/v1/devices/{device_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_delete_device(client):
    create_resp = client.post("/api/v1/devices/", json={"name": "Delete Me"})
    device_id = create_resp.json()["id"]

    response = client.delete(f"/api/v1/devices/{device_id}")
    assert response.status_code == 200

    # Verify it's gone
    get_resp = client.get(f"/api/v1/devices/{device_id}")
    assert get_resp.status_code == 404

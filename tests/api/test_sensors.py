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


@pytest.fixture
def created_sensor(db_session, created_zone):
    sensor = SensorModel(
        name="Test Sensor",
        type="humidity",
        unit="%",
        is_active=True,
        zone_id=created_zone.id,
    )
    db_session.add(sensor)
    db_session.commit()
    db_session.refresh(sensor)
    return sensor


def test_create_sensor(client, created_zone):
    response = client.post(
        "/sensors/",
        json={
            "name": "New Sensor",
            "type": "temperature",
            "unit": "C",
            "is_active": True,
            "zone_id": str(created_zone.id),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Sensor"
    assert data["zone_id"] == str(created_zone.id)
    assert "id" in data


def test_read_sensors(client, created_sensor):
    response = client.get("/sensors/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    ids = [s["id"] for s in data]
    assert str(created_sensor.id) in ids


def test_read_sensor(client, created_sensor):
    response = client.get(f"/sensors/{created_sensor.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(created_sensor.id)
    assert data["name"] == created_sensor.name


def test_update_sensor(client, created_sensor):
    new_name = "Updated Sensor Name"
    response = client.put(f"/sensors/{created_sensor.id}", json={"name": new_name})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name
    assert data["id"] == str(created_sensor.id)


def test_delete_sensor(client, created_sensor):
    response = client.delete(f"/sensors/{created_sensor.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(created_sensor.id)
    assert data["deleted_at"] is not None

    # Verify lookup fails
    response = client.get(f"/sensors/{created_sensor.id}")
    assert response.status_code == 404


def test_create_sensor_invalid_parent(client):
    # Should fail if neither plant_id nor zone_id is provided, OR both are provided.
    # The model has a check constraint: ((plant_id is not null) + (zone_id is not null)) = 1
    response = client.post(
        "/sensors/",
        json={
            "name": "Invalid Sensor",
            "type": "temperature",
            "unit": "C",
            "is_active": True,
        },
    )
    assert response.status_code == 400

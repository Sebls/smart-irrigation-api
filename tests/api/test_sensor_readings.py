import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime

from app.main import app
from app.infrastructure.db.base import Base
from app.api.dependencies import get_db
from app.infrastructure.models.zones import ZoneModel
from app.infrastructure.models.sensors import SensorModel
from app.infrastructure.models.sensor_readings import SensorReadingModel

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


@pytest.fixture
def created_reading(db_session, created_sensor):
    reading = SensorReadingModel(
        sensor_id=created_sensor.id,
        value=25.5,
        recorded_at=datetime.utcnow(),
    )
    db_session.add(reading)
    db_session.commit()
    db_session.refresh(reading)
    return reading


def test_create_sensor_reading(client, created_sensor):
    response = client.post(
        "/api/v1/sensor-readings/",
        json={
            "sensor_id": str(created_sensor.id),
            "value": 30.2,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["value"] == 30.2
    assert data["sensor_id"] == str(created_sensor.id)
    assert "id" in data


def test_read_sensor_readings(client, created_reading):
    response = client.get("/api/v1/sensor-readings/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    ids = [r["id"] for r in data]
    assert str(created_reading.id) in ids


def test_read_sensor_readings_by_sensor(client, created_reading):
    response = client.get(
        f"/api/v1/sensor-readings/?sensor_id={created_reading.sensor_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["sensor_id"] == str(created_reading.sensor_id)


def test_read_sensor_reading(client, created_reading):
    response = client.get(f"/api/v1/sensor-readings/{created_reading.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(created_reading.id)
    assert data["value"] == created_reading.value


def test_delete_sensor_reading(client, created_reading):
    response = client.delete(f"/api/v1/sensor-readings/{created_reading.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(created_reading.id)

    # Verify lookup fails
    response = client.get(f"/api/v1/sensor-readings/{created_reading.id}")
    assert response.status_code == 404

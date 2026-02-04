import pytest
import uuid
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


def test_save_telemetry_by_id(client, sensors):
    s1 = sensors[0]
    device_id = str(uuid.uuid4())
    telemetry_data = {
        "sentAt": "2026-01-26T12:00:00.000Z",
        "readings": [
            {"sensorId": str(s1.id), "type": "humidity", "value": 80.0, "unit": "%"}
        ],
    }

    response = client.post(
        f"/api/v1/devices/{device_id}/telemetry", json=telemetry_data
    )
    assert response.status_code == 201
    data = response.json()
    assert data["processedCount"] == 1
    assert data["deviceId"] == device_id


def test_save_telemetry_unknown_id(client, sensors):
    # Test that name or random string doesn't save data
    device_id = str(uuid.uuid4())
    telemetry_data = {
        "sentAt": "2026-01-26T12:00:00.000Z",
        "readings": [
            {
                "sensorId": "s-1-1-1",  # This is a name, but we expect UUID only now
                "type": "humidity",
                "value": 74.1,
                "unit": "%",
            },
            {
                "sensorId": str(uuid.uuid4()),  # Valid UUID but non-existent
                "type": "temperature",
                "value": 24.3,
                "unit": "C",
            },
        ],
    }

    response = client.post(
        f"/api/v1/devices/{device_id}/telemetry", json=telemetry_data
    )
    assert response.status_code == 201
    data = response.json()
    assert data["processedCount"] == 0

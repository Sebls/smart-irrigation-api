import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.infrastructure.db.base import Base
from app.api.dependencies import get_db
from app.infrastructure.models.devices import DeviceModel
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


def test_provision_device_new(client, db_session):
    payload = {
        "hardwareId": "raspi-test-001",
        "firmware": "1.0.0",
        "capabilities": {
            "sensors": [
                {"localName": "soil_1", "type": "humidity"},
                {"localName": "flow_main", "type": "flow"},
            ],
            "cameras": ["front_cam"],
        },
    }

    response = client.post("/api/v1/devices/provision", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "deviceId" in data
    assert len(data["sensors"]) == 2
    assert data["sensors"][0]["localName"] == "soil_1"
    assert data["sensors"][1]["localName"] == "flow_main"

    # Verify DB state
    device = (
        db_session.query(DeviceModel)
        .filter(DeviceModel.hardware_id == "raspi-test-001")
        .first()
    )
    assert device is not None
    assert device.id == uuid.UUID(data["deviceId"])

    zone = db_session.query(ZoneModel).filter(ZoneModel.name == "Primary Zone").first()
    assert zone is not None

    sensors = db_session.query(SensorModel).filter(SensorModel.zone_id == zone.id).all()
    assert len(sensors) == 2


def test_provision_device_idempotency(client, db_session):
    payload = {
        "hardwareId": "raspi-test-002",
        "firmware": "1.0.0",
        "capabilities": {"sensors": [{"localName": "soil_1", "type": "humidity"}]},
    }

    # First provision
    resp1 = client.post("/api/v1/devices/provision", json=payload)
    assert resp1.status_code == 200
    id1 = resp1.json()["deviceId"]

    # Second provision (same hardware ID)
    resp2 = client.post("/api/v1/devices/provision", json=payload)
    assert resp2.status_code == 200
    id2 = resp2.json()["deviceId"]

    assert id1 == id2

    # Verify no duplicate devices or zones
    devices_count = (
        db_session.query(DeviceModel)
        .filter(DeviceModel.hardware_id == "raspi-test-002")
        .count()
    )
    assert devices_count == 1

    zones_count = (
        db_session.query(ZoneModel).filter(ZoneModel.name == "Primary Zone").count()
    )
    assert zones_count == 1

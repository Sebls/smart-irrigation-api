import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime
from decimal import Decimal

from app.main import app
from app.infrastructure.db.base import Base
from app.api.dependencies import get_db
from app.infrastructure.models.water import WaterTankModel, WaterTankReadingModel

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
def created_tank(db_session):
    tank = WaterTankModel(name="Main Tank", capacity_liters=1000)
    db_session.add(tank)
    db_session.commit()
    db_session.refresh(tank)
    return tank


@pytest.fixture
def created_reading(db_session, created_tank):
    reading = WaterTankReadingModel(
        tank_id=created_tank.id,
        level_percent=Decimal("80.5"),
        current_liters=Decimal("805.0"),
        recorded_at=datetime.utcnow(),
    )
    db_session.add(reading)
    db_session.commit()
    db_session.refresh(reading)
    return reading


# Tank Tests
def test_create_tank(client):
    response = client.post(
        "/water/tanks/",
        json={"name": "New Tank", "capacity_liters": 500},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Tank"
    assert data["capacity_liters"] == 500
    assert "id" in data


def test_read_tanks(client, created_tank):
    response = client.get("/water/tanks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    ids = [t["id"] for t in data]
    assert str(created_tank.id) in ids


def test_update_tank(client, created_tank):
    new_name = "Updated Tank Name"
    response = client.put(f"/water/tanks/{created_tank.id}", json={"name": new_name})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name


def test_delete_tank(client, created_tank):
    response = client.delete(f"/water/tanks/{created_tank.id}")
    assert response.status_code == 200
    assert response.json()["deleted_at"] is not None


# Reading Tests
def test_create_tank_reading(client, created_tank):
    response = client.post(
        "/water/readings/",
        json={
            "tank_id": str(created_tank.id),
            "level_percent": "75.0",
            "current_liters": "750.0",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert (
        data["level_percent"] == "75.00"
    )  # Numeric(5,2) usually returns 2 decimal places as string or Decimal
    assert "id" in data


def test_read_tank_readings(client, created_reading):
    response = client.get(f"/water/readings/?tank_id={created_reading.tank_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["tank_id"] == str(created_reading.tank_id)

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
from app.infrastructure.models.activity import ActivityEventModel

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
def created_event(db_session, created_zone):
    event = ActivityEventModel(
        type="info",
        message="System started",
        zone_id=created_zone.id,
        occurred_at=datetime.utcnow(),
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


def test_create_activity_event(client, created_zone):
    response = client.post(
        "/activity/",
        json={
            "type": "warning",
            "message": "Low water level",
            "zone_id": str(created_zone.id),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Low water level"
    assert data["zone_id"] == str(created_zone.id)
    assert "id" in data


def test_read_activity_events(client, created_event):
    response = client.get("/activity/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    ids = [e["id"] for e in data]
    assert str(created_event.id) in ids


def test_read_activity_events_filter(client, created_event):
    response = client.get(f"/activity/?type={created_event.type}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["type"] == created_event.type


def test_read_activity_event(client, created_event):
    response = client.get(f"/activity/{created_event.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(created_event.id)
    assert data["message"] == created_event.message


def test_delete_activity_event(client, created_event):
    response = client.delete(f"/activity/{created_event.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(created_event.id)

    # Verify lookup fails
    response = client.get(f"/activity/{created_event.id}")
    assert response.status_code == 404

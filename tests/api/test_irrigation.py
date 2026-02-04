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
from app.infrastructure.models.irrigation import IrrigationJobModel

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
def created_job(db_session, created_zone):
    job = IrrigationJobModel(
        scope="zone",
        zone_id=created_zone.id,
        action="start",
        duration_seconds=300,
        status="accepted",
        requested_at=datetime.utcnow(),
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


def test_create_irrigation_job(client, created_zone):
    response = client.post(
        "/api/v1/irrigation/",
        json={
            "scope": "zone",
            "zone_id": str(created_zone.id),
            "action": "start",
            "duration_seconds": 600,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["scope"] == "zone"
    assert data["zone_id"] == str(created_zone.id)
    assert "id" in data


def test_read_irrigation_jobs(client, created_job):
    response = client.get("/api/v1/irrigation/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    ids = [j["id"] for j in data]
    assert str(created_job.id) in ids


def test_update_irrigation_job(client, created_job):
    new_status = "running"
    response = client.put(
        f"/api/v1/irrigation/{created_job.id}", json={"status": new_status}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == new_status


def test_delete_irrigation_job(client, created_job):
    response = client.delete(f"/api/v1/irrigation/{created_job.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(created_job.id)

    # Verify lookup fails
    response = client.get(f"/api/v1/irrigation/{created_job.id}")
    assert response.status_code == 404

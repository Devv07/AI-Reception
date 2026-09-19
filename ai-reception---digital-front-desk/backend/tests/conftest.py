import os
from collections.abc import Generator
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "test-secret-for-local-tests-32-bytes"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models import Department, Organization, User, Visitor
from app.security import hash_password

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def database() -> Generator[None, None, None]:
    Base.metadata.create_all(engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def seed_data() -> dict[str, object]:
    db = TestingSessionLocal()
    organization = Organization(id=uuid4(), name="Test Organization", slug=f"test-{uuid4().hex[:8]}")
    db.add(organization)
    db.flush()
    department = Department(organization_id=organization.id, name="Admissions", active=True)
    visitor = Visitor(organization_id=organization.id, name="Visitor", email=f"visitor-{uuid4().hex[:8]}@example.com")
    db.add_all([department, visitor])
    db.flush()
    admin = User(organization_id=organization.id, name="Admin", email=f"admin-{uuid4().hex[:8]}@example.com", password_hash=hash_password("admin-pass"), role="admin")
    reception = User(organization_id=organization.id, name="Reception", email=f"reception-{uuid4().hex[:8]}@example.com", password_hash=hash_password("reception-pass"), role="reception")
    other_organization = Organization(id=uuid4(), name="Other Organization", slug=f"other-{uuid4().hex[:8]}")
    other_admin = User(organization_id=other_organization.id, name="Other Admin", email=f"other-admin-{uuid4().hex[:8]}@example.com", password_hash=hash_password("other-pass"), role="admin")
    db.add_all([admin, reception, other_organization, other_admin])
    db.commit()
    data = {"organization": organization, "department": department, "visitor": visitor, "admin": admin, "reception": reception, "other_organization": other_organization, "other_admin": other_admin}
    db.close()
    return data


def login(client: TestClient, user: User, password: str) -> str:
    response = client.post("/api/v1/auth/login", json={"email": user.email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]

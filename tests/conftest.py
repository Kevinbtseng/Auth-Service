import os

os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@127.0.0.1:5433/auth_test"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.database import Base, engine, SessionLocal
from app.redis_client import r
from app import models, crud, schemas

assert engine.url.database == "auth_test"
assert r.connection_pool.connection_kwargs["db"] == 1

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(autouse=True)
def clean_state():
    r.flushdb()
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE users RESTART IDENTITY CASCADE"))

@pytest.fixture
def registered_user():
    email, password = "johndoe@gmail.com", "Secret123!"
    with SessionLocal() as db:
        crud.create_user(db,
                         schemas.UserCreate(email=email, password=password))
    return {"email": email, "password": password}

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def login_tokens(client, registered_user):
    resp = client.post("/auth/login", json=registered_user)
    assert resp.status_code == 200
    return resp.json()
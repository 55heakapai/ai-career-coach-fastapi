import os
import tempfile

os.environ["LLM_PROVIDER"] = "mock"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-long-enough-for-hs256"
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db.session import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)  # fresh tables for every test
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth(client):
    res = client.post("/api/auth/register", json={"name": "Asha", "email": "asha@example.com", "password": "correct-horse"})
    assert res.status_code == 201
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

@pytest.fixture(scope="function")
def app_with_tmp_db(tmp_path):
    # Point the app to a fresh, per-test SQLite file
    test_db = tmp_path / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{test_db}"

    # Create tables on that DB
    from app.db.init_db import init_db
    init_db()

    # Import app AFTER setting env and initializing DB
    from app.main import app
    return app

@pytest_asyncio.fixture(scope="function")
async def asgi_client(app_with_tmp_db):
    # httpx >= 0.28: mount FastAPI app via ASGITransport
    transport = ASGITransport(app=app_with_tmp_db)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
import pytest
import random
import string

def _rand_email():
    token = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"u_{token}@example.com"

@pytest.fixture
def user_factory(client):
    created = []
    def _make():
        payload = {"email": _rand_email(), "name": "Test User"}
        r = client.post("/api/users/", json=payload)
        assert r.status_code == 201, r.text
        data = r.json()
        created.append(data)
        return data
    return _make
# --- sync httpx client over ASGITransport, using the temp DB app fixture ---
import pytest
from starlette.testclient import TestClient

@pytest.fixture
def client(app_with_tmp_db):
    with TestClient(app_with_tmp_db, base_url="http://testserver") as c:
        yield c
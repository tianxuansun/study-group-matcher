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

import pytest

@pytest.mark.asyncio
async def test_create_and_get_user(asgi_client):
    # Create
    resp = await asgi_client.post("/api/users/", json={"email": "t1@demo.edu", "name": "Test1"})
    assert resp.status_code == 201, resp.text
    data = resp.json()
    uid = data["id"]
    assert data["email"] == "t1@demo.edu"

    # List
    resp = await asgi_client.get("/api/users/")
    assert resp.status_code == 200, resp.text
    users = resp.json()
    assert any(u["id"] == uid for u in users)

    # Get by id
    resp = await asgi_client.get(f"/api/users/{uid}")
    assert resp.status_code == 200, resp.text
    one = resp.json()
    assert one["id"] == uid

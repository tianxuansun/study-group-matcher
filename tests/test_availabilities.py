import pytest

@pytest.mark.asyncio
async def test_availability_crud(asgi_client):
    # Need a user first
    resp = await asgi_client.post("/api/users/", json={"email": "a1@demo.edu", "name": "A1"})
    assert resp.status_code == 201, resp.text
    user_id = resp.json()["id"]

    # Create availability
    payload = {"user_id": user_id, "weekday": 2, "start_min": 600, "end_min": 660}
    resp = await asgi_client.post("/api/availabilities/", json=payload)
    assert resp.status_code == 201, resp.text
    av = resp.json()
    aid = av["id"]
    assert av["weekday"] == 2 and av["start_min"] == 600

    # List (filter by user)
    resp = await asgi_client.get(f"/api/availabilities/?user_id={user_id}")
    assert resp.status_code == 200
    arr = resp.json()
    assert any(x["id"] == aid for x in arr)

    # Get by id
    resp = await asgi_client.get(f"/api/availabilities/{aid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == aid

    # Update
    resp = await asgi_client.patch(f"/api/availabilities/{aid}", json={"end_min": 690})
    assert resp.status_code == 200
    assert resp.json()["end_min"] == 690

    # Delete
    resp = await asgi_client.delete(f"/api/availabilities/{aid}")
    assert resp.status_code == 204

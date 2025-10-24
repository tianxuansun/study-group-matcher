import pytest

@pytest.mark.asyncio
async def test_group_list_filters(asgi_client):
    await asgi_client.post("/api/groups/", json={"name": "Partial Option A"})
    await asgi_client.post("/api/groups/", json={"name": "Partial Option B"})
    await asgi_client.post("/api/groups/", json={"name": "Other Prefix"})

    r = await asgi_client.get("/api/groups/?name_prefix=Partial%20Option&limit=50")
    assert r.status_code == 200
    names = [g["name"] for g in r.json()]
    assert set(names) == {"Partial Option A", "Partial Option B"}

@pytest.mark.asyncio
async def test_membership_list_filters(asgi_client):
    # seed minimal user+groups
    u = await asgi_client.post("/api/users/", json={"email": "f1@demo.edu", "name":"F1"})
    uid = u.json()["id"]
    g1 = (await asgi_client.post("/api/groups/", json={"name": "F-1"})).json()["id"]
    g2 = (await asgi_client.post("/api/groups/", json={"name": "F-2"})).json()["id"]
    await asgi_client.post("/api/memberships/", json={"user_id": uid, "group_id": g1})
    await asgi_client.post("/api/memberships/", json={"user_id": uid, "group_id": g2})

    r = await asgi_client.get(f"/api/memberships/?user_id={uid}&limit=50")
    assert r.status_code == 200
    arr = r.json()
    assert len(arr) == 2

    r = await asgi_client.get(f"/api/memberships/?group_id={g1}&limit=50")
    assert r.status_code == 200
    arr = r.json()
    assert all(m["group_id"] == g1 for m in arr)

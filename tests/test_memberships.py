import pytest

@pytest.mark.asyncio
async def test_membership_crud(asgi_client):
    # seed user + group
    r = await asgi_client.post("/api/users/", json={"email": "g1@demo.edu", "name": "G1"})
    assert r.status_code == 201
    user_id = r.json()["id"]

    r = await asgi_client.post("/api/groups/", json={"name": "G-Alpha"})
    assert r.status_code == 201
    group_id = r.json()["id"]

    # create membership
    r = await asgi_client.post("/api/memberships/", json={"user_id": user_id, "group_id": group_id})
    assert r.status_code == 201, r.text
    m = r.json()
    mid = m["id"]

    # list + pagination
    r = await asgi_client.get("/api/memberships/?limit=20&offset=0")
    assert r.status_code == 200
    arr = r.json()
    assert any(x["id"] == mid for x in arr)

    # get by id
    r = await asgi_client.get(f"/api/memberships/{mid}")
    assert r.status_code == 200
    assert r.json()["id"] == mid

    # update to new group
    r = await asgi_client.post("/api/groups/", json={"name": "G-Beta"})
    assert r.status_code == 201
    new_gid = r.json()["id"]

    r = await asgi_client.patch(f"/api/memberships/{mid}", json={"group_id": new_gid})
    assert r.status_code == 200
    assert r.json()["group_id"] == new_gid

    # conflict on duplicate (same user/group)
    r_dup = await asgi_client.post("/api/memberships/", json={"user_id": user_id, "group_id": new_gid})
    assert r_dup.status_code == 409

    # delete
    r = await asgi_client.delete(f"/api/memberships/{mid}")
    assert r.status_code == 204

    # 404 after delete
    r = await asgi_client.get(f"/api/memberships/{mid}")
    assert r.status_code == 404

@pytest.mark.asyncio
async def test_membership_create_404s(asgi_client):
    r = await asgi_client.post("/api/memberships/", json={"user_id": 999999, "group_id": 1})
    assert r.status_code == 404
    r = await asgi_client.post("/api/memberships/", json={"user_id": 1, "group_id": 999999})
    assert r.status_code == 404
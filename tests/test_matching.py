import pytest

def make_user(asgi_client, i):
    return pytest.run(asyncio=False)  # just to help IDEs

@pytest.mark.asyncio
async def test_matching_preview_and_apply(asgi_client):
    # Create 6 users with the same Mon 10:00-12:00 availability
    user_ids = []
    for i in range(6):
        r = await asgi_client.post("/api/users/", json={"email": f"m{i}@demo.edu", "name": f"M{i}"})
        assert r.status_code == 201, r.text
        uid = r.json()["id"]
        user_ids.append(uid)
        av = {"user_id": uid, "weekday": 0, "start_min": 600, "end_min": 720}  # Mon 10:00-12:00
        r = await asgi_client.post("/api/availabilities/", json=av)
        assert r.status_code == 201, r.text

    # Preview: group_size 3, at least 60 minutes overlap -> expect two groups of 3
    payload = {"user_ids": user_ids, "group_size": 3, "min_overlap_minutes": 60}
    r = await asgi_client.post("/api/matching/preview/", json=payload)
    assert r.status_code == 200, r.text
    plan = r.json()
    assert len(plan["groups"]) == 2
    assert plan["leftovers"] == []

    # Apply: should create groups + memberships
    r = await asgi_client.post("/api/matching/apply/", json=payload)
    assert r.status_code == 201, r.text
    applied = r.json()
    assert len(applied["groups"]) == 2

    # Verify groups exist and have 3 members
    r = await asgi_client.get("/api/groups/?limit=100")
    assert r.status_code == 200
    groups = r.json()
    # pick the two newest auto groups by name
    auto = [g for g in groups if g["name"].startswith("Auto Group")]
    assert len(auto) >= 2
    # We can't rely on order in DB; just ensure memberships exist through listing
    r = await asgi_client.get("/api/memberships/?limit=100")
    assert r.status_code == 200
    mids = r.json()
    # count per group
    counts = {}
    for m in mids:
        counts[m["group_id"]] = counts.get(m["group_id"], 0) + 1
    # at least two groups should have size 3
    assert sum(1 for c in counts.values() if c == 3) >= 2

@pytest.mark.asyncio
async def test_matching_handles_leftovers(asgi_client):
    # 5 users -> group_size 3 → one group of 3, 2 leftovers
    user_ids = []
    for i in range(5):
        r = await asgi_client.post("/api/users/", json={"email": f"x{i}@demo.edu", "name": f"X{i}"})
        uid = r.json()["id"]
        user_ids.append(uid)
        # Wed 14:00-16:00
        r = await asgi_client.post("/api/availabilities/", json={"user_id": uid, "weekday": 2, "start_min": 840, "end_min": 960})
        assert r.status_code == 201

    payload = {"user_ids": user_ids, "group_size": 3, "min_overlap_minutes": 60}
    r = await asgi_client.post("/api/matching/preview/", json=payload)
    assert r.status_code == 200
    plan = r.json()
    assert len(plan["groups"]) == 1
    assert len(plan["groups"][0]["user_ids"]) == 3
    assert len(plan["leftovers"]) == 2
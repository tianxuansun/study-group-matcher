import pytest

import pytest

@pytest.mark.asyncio
async def test_matching_allows_partial_group(asgi_client):
    # 5 users with identical Wed 14:00-16:00 availability
    user_ids = []
    for i in range(5):
        r = await asgi_client.post("/api/users/", json={"email": f"p{i}@demo.edu", "name": f"P{i}"} )
        assert r.status_code == 201, r.text
        uid = r.json()["id"]
        user_ids.append(uid)
        r = await asgi_client.post("/api/availabilities/", json={"user_id": uid, "weekday": 2, "start_min": 840, "end_min": 960})
        assert r.status_code == 201, r.text

    payload = {
        "user_ids": user_ids,
        "group_size": 3,
        "min_overlap_minutes": 60,
        "allow_partial_last_group": True,
        "name_prefix": "Partial Option"  # unique prefix to isolate this test
    }

    # Preview should return one full group (3) + one partial group (2)
    r = await asgi_client.post("/api/matching/preview/", json=payload)
    assert r.status_code == 200, r.text
    plan = r.json()
    sizes = sorted(len(g["user_ids"]) for g in plan["groups"])
    assert sizes == [2, 3]

    # Apply should create memberships for all 5 users across exactly those 2 groups
    r = await asgi_client.post("/api/matching/apply/", json=payload)
    assert r.status_code == 201, r.text

    # Fetch ONLY the groups created by this test (by name prefix)
    r = await asgi_client.get("/api/groups/?limit=100")
    assert r.status_code == 200
    test_group_ids = [g["id"] for g in r.json() if g["name"].startswith("Partial Option")]

    r = await asgi_client.get("/api/memberships/?limit=100")
    assert r.status_code == 200
    mids = r.json()

    counts = {}
    for m in mids:
        if m["group_id"] in test_group_ids:
            counts[m["group_id"]] = counts.get(m["group_id"], 0) + 1

    # Exactly one partial group (2) and one full group (3)
    assert sorted(counts.values()) == [2, 3]


@pytest.mark.asyncio
async def test_matching_name_prefix(asgi_client):
    # 3 users, one group, custom prefix
    user_ids = []
    for i in range(3):
        r = await asgi_client.post("/api/users/", json={"email": f"np{i}@demo.edu", "name": f"NP{i}"} )
        uid = r.json()["id"]
        user_ids.append(uid)
        r = await asgi_client.post("/api/availabilities/", json={"user_id": uid, "weekday": 0, "start_min": 600, "end_min": 720})
        assert r.status_code == 201

    payload = {
        "user_ids": user_ids,
        "group_size": 3,
        "min_overlap_minutes": 60,
        "name_prefix": "CMP SCI 101 Group"
    }

    r = await asgi_client.post("/api/matching/apply/", json=payload)
    assert r.status_code == 201, r.text

    r = await asgi_client.get("/api/groups/?limit=100")
    assert r.status_code == 200
    names = [g["name"] for g in r.json()]
    assert any(n.startswith("CMP SCI 101 Group") for n in names)

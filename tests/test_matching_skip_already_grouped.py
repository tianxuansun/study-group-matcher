import pytest

@pytest.mark.asyncio
async def test_skip_already_grouped_in_by_course(asgi_client):
    # Create course
    rc = await asgi_client.post("/api/courses/", json={"code": "HIST10", "title": "History"})
    course_id = rc.json()["id"]

    # Make 4 users, enroll all, identical availability
    uids = []
    for i in range(4):
        ru = await asgi_client.post("/api/users/", json={"email": f"h{i}@demo.edu", "name": f"H{i}"})
        uid = ru.json()["id"]
        uids.append(uid)
        await asgi_client.post("/api/enrollments/", json={"user_id": uid, "course_id": course_id})
        await asgi_client.post("/api/availabilities/", json={"user_id": uid, "weekday": 1, "start_min": 600, "end_min": 720})

    # Put two users into an existing group for this course
    rg = await asgi_client.post("/api/groups/", json={"name": "HIST10-G1", "course_id": course_id})
    gid = rg.json()["id"]
    for uid in uids[:2]:
        await asgi_client.post("/api/memberships/", json={"user_id": uid, "group_id": gid})

    # Now preview-by-course with group_size=2 and skip_already_grouped=True (default)
    payload = {"group_size": 2, "min_overlap_minutes": 60}
    r = await asgi_client.post(f"/api/matching/preview/by-course/{course_id}/", json=payload)
    assert r.status_code == 200, r.text
    plan = r.json()
    # Should only consider the remaining two users
    assert len(plan["groups"]) == 1
    assert sorted(plan["groups"][0]["user_ids"]) == sorted(uids[2:])

    # Apply should create a new group of the remaining two
    r = await asgi_client.post(f"/api/matching/apply/by-course/{course_id}/", json=payload)
    assert r.status_code == 201, r.text

    # Verify we have memberships for all 4 users in this course across 2 groups
    r = await asgi_client.get("/api/memberships/?limit=100")
    assert r.status_code == 200
    mids = r.json()
    by_group = {}
    for m in mids:
        by_group[m["group_id"]] = by_group.get(m["group_id"], 0) + 1
    # Two groups with 2 members each
    assert sorted([c for c in by_group.values() if c in (2, 3)])[:2] == [2, 2]

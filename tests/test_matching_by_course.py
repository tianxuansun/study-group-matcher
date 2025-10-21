import pytest

@pytest.mark.asyncio
async def test_matching_by_course_preview_and_apply(asgi_client):
    # create a course and 6 users w/ same slot
    rc = await asgi_client.post("/api/courses/", json={"code": "MATH200", "title": "Math"})
    course_id = rc.json()["id"]

    user_ids = []
    for i in range(6):
        ru = await asgi_client.post("/api/users/", json={"email": f"m{i}@c.edu", "name": f"M{i}"})
        uid = ru.json()["id"]
        user_ids.append(uid)
        # enroll
        r = await asgi_client.post("/api/enrollments/", json={"user_id": uid, "course_id": course_id})
        assert r.status_code == 201
        # availability Mon 10-12
        r = await asgi_client.post("/api/availabilities/", json={"user_id": uid, "weekday": 0, "start_min": 600, "end_min": 720})
        assert r.status_code == 201

    # preview by course: group_size 3
    payload = {"group_size": 3, "min_overlap_minutes": 60}
    r = await asgi_client.post(f"/api/matching/preview/by-course/{course_id}/", json=payload)
    assert r.status_code == 200, r.text
    plan = r.json()
    assert len(plan["groups"]) == 2
    assert plan["leftovers"] == []

    # apply
    r = await asgi_client.post(f"/api/matching/apply/by-course/{course_id}/", json=payload)
    assert r.status_code == 201, r.text

    # verify memberships got created
    r = await asgi_client.get("/api/memberships/?limit=100")
    assert r.status_code == 200
    mids = r.json()
    # expect two groups with 3 members each
    counts = {}
    for m in mids:
        counts[m["group_id"]] = counts.get(m["group_id"], 0) + 1
    assert sum(1 for c in counts.values() if c == 3) >= 2

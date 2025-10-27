import pytest

@pytest.mark.asyncio
async def test_stats_overview_per_course(asgi_client):
    # Course + 5 users, enroll all, same slot
    rc = await asgi_client.post("/api/courses/", json={"code": "STAT100", "title": "Stats"})
    course_id = rc.json()["id"]

    uids = []
    for i in range(5):
        ru = await asgi_client.post("/api/users/", json={"email": f"s{i}@demo.edu", "name": f"S{i}"})
        uid = ru.json()["id"]
        uids.append(uid)
        await asgi_client.post("/api/enrollments/", json={"user_id": uid, "course_id": course_id})
        await asgi_client.post("/api/availabilities/", json={"user_id": uid, "weekday": 2, "start_min": 840, "end_min": 960})

    # Make pairs (2+2) and leave one ungrouped
    payload = {"group_size": 2, "min_overlap_minutes": 60}
    r = await asgi_client.post(f"/api/matching/apply/by-course/{course_id}/", json=payload)
    assert r.status_code == 201, r.text

    # Hit stats
    r = await asgi_client.get("/api/stats/overview")
    assert r.status_code == 200
    data = r.json()
    assert "totals" in data and "per_course" in data

    entry = next(pc for pc in data["per_course"] if pc["course_id"] == course_id)
    assert entry["enrolled"] == 5
    assert entry["groups"] == 2
    assert entry["members_in_groups"] == 4
    assert entry["ungrouped_enrolled"] == 1
    assert entry["avg_group_size"] == 2.0

import pytest

@pytest.mark.asyncio
async def test_course_groups_csv_and_group_roster_csv(asgi_client):
    rc = await asgi_client.post("/api/courses/", json={"code": "BIO101", "title": "Bio"})
    course_id = rc.json()["id"]

    # 3 users -> one group of 3
    uids = []
    for i in range(3):
        ru = await asgi_client.post("/api/users/", json={"email": f"b{i}@demo.edu", "name": f"B{i}"})
        uid = ru.json()["id"]
        uids.append(uid)
        await asgi_client.post("/api/enrollments/", json={"user_id": uid, "course_id": course_id})
        await asgi_client.post("/api/availabilities/", json={"user_id": uid, "weekday": 1, "start_min": 600, "end_min": 720})

    payload = {"group_size": 3, "min_overlap_minutes": 60}
    r = await asgi_client.post(f"/api/matching/apply/by-course/{course_id}/", json=payload)
    assert r.status_code == 201, r.text

    # Fetch created group id via filter
    r = await asgi_client.get(f"/api/groups/?course_id={course_id}&limit=50")
    assert r.status_code == 200
    groups = r.json()
    assert len(groups) >= 1
    group_id = groups[0]["id"]

    # Course CSV
    r = await asgi_client.get(f"/api/exports/courses/{course_id}/groups.csv")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    lines = r.text.strip().splitlines()
    assert lines[0].startswith("group_id,group_name,user_id,user_email,user_name")
    # Expect header + 3 members rows
    assert len(lines) >= 4

    # Group roster CSV
    r = await asgi_client.get(f"/api/exports/groups/{group_id}/roster.csv")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    glines = r.text.strip().splitlines()
    assert glines[0].startswith("user_id,user_email,user_name")
    assert len(glines) == 4  # header + 3 members

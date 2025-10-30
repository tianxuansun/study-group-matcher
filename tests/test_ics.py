# tests/test_ics.py
import pytest

@pytest.mark.asyncio
async def test_group_schedule_ics(asgi_client):
    # seed a course and one scheduled group
    rc = await asgi_client.post("/api/courses/", json={"code": "ICS101", "title": "ICS Course"})
    course_id = rc.json()["id"]

    # Create a group with schedule (Wed 14:00–15:00)
    rg = await asgi_client.post("/api/groups/", json={
        "name": "ICS-Group-1",
        "course_id": course_id,
        "meeting_weekday": 2,         # Wed
        "meeting_start_min": 14 * 60,
        "meeting_end_min": 15 * 60
    })
    assert rg.status_code == 201, rg.text
    group_id = rg.json()["id"]

    r = await asgi_client.get(f"/api/exports/groups/{group_id}/schedule.ics")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("text/calendar")
    body = r.text
    assert "BEGIN:VCALENDAR" in body
    assert "BEGIN:VEVENT" in body
    assert "RRULE:FREQ=WEEKLY;BYDAY=WE" in body  # 2 -> WE
    assert "DURATION:PT60M" in body

@pytest.mark.asyncio
async def test_course_schedules_ics(asgi_client):
    # two scheduled groups under one course
    rc = await asgi_client.post("/api/courses/", json={"code": "ICS200", "title": "ICS Course 2"})
    course_id = rc.json()["id"]

    for name, wd in [("G-A", 0), ("G-B", 4)]:  # Mon & Fri
        rg = await asgi_client.post("/api/groups/", json={
            "name": name,
            "course_id": course_id,
            "meeting_weekday": wd,
            "meeting_start_min": 10 * 60,
            "meeting_end_min": 11 * 60
        })
        assert rg.status_code == 201, rg.text

    r = await asgi_client.get(f"/api/exports/courses/{course_id}/schedules.ics")
    assert r.status_code == 200, r.text
    body = r.text
    # Two events present
    assert body.count("BEGIN:VEVENT") == 2

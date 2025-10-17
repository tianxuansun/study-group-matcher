import random

def test_users_404(client):
    r = client.get("/api/users/999999/")
    assert r.status_code == 404

def test_courses_404(client):
    r = client.get("/api/courses/999999/")
    assert r.status_code == 404

def test_availabilities_404(client):
    r = client.get("/api/availabilities/999999/")
    assert r.status_code == 404

def test_availability_weekday_out_of_range(client, user_factory):
    user = user_factory()
    payload = {
        "user_id": user["id"],
        "weekday": 7,           # invalid
        "start_min": 540,
        "end_min": 600
    }
    r = client.post("/api/availabilities/", json=payload)
    # FastAPI/Pydantic will raise 422 for validation error
    assert r.status_code in (400, 422)

def test_availability_end_not_after_start(client, user_factory):
    user = user_factory()
    payload = {
        "user_id": user["id"],
        "weekday": 2,
        "start_min": 600,
        "end_min": 600      # invalid: equal
    }
    r = client.post("/api/availabilities/", json=payload)
    assert r.status_code in (400, 422)

def test_course_code_unique_conflict(client):
    payload = {"code": "CS-TEST", "title": "Title 1"}
    r1 = client.post("/api/courses/", json=payload)
    assert r1.status_code == 201

    # try duplicate code
    payload2 = {"code": "CS-TEST", "title": "Title 2"}
    r2 = client.post("/api/courses/", json=payload2)
    # our API raises 409 via errors.conflict(...)
    assert r2.status_code == 409

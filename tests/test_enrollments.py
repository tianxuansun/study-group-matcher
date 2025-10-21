import pytest

@pytest.mark.asyncio
async def test_enrollment_crud(asgi_client):
    # create user + course
    ru = await asgi_client.post("/api/users/", json={"email": "e1@demo.edu", "name": "E1"})
    rc = await asgi_client.post("/api/courses/", json={"code": "CSE101", "title": "Intro"})
    user_id = ru.json()["id"]
    course_id = rc.json()["id"]

    # enroll
    r = await asgi_client.post("/api/enrollments/", json={"user_id": user_id, "course_id": course_id})
    assert r.status_code == 201, r.text
    assert r.json() == {"user_id": user_id, "course_id": course_id}

    # duplicate -> 409
    r = await asgi_client.post("/api/enrollments/", json={"user_id": user_id, "course_id": course_id})
    assert r.status_code == 409

    # list by user
    r = await asgi_client.get(f"/api/enrollments/?user_id={user_id}")
    assert r.status_code == 200
    assert any(x["course_id"] == course_id for x in r.json())
    assert "X-Total-Count" in r.headers

    # list by course
    r = await asgi_client.get(f"/api/enrollments/?course_id={course_id}")
    assert r.status_code == 200
    assert any(x["user_id"] == user_id for x in r.json())

    # delete
    r = await asgi_client.delete(f"/api/enrollments/{user_id}/{course_id}")
    assert r.status_code == 204

    # delete again -> 404
    r = await asgi_client.delete(f"/api/enrollments/{user_id}/{course_id}")
    assert r.status_code == 404

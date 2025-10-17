def test_users_pagination(client):
    # Create 30 users
    for i in range(30):
        r = client.post("/api/users/", json={"email": f"u{i}@example.com", "name": f"U{i}"})
        assert r.status_code == 201

    r = client.get("/api/users/?limit=5&offset=10")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 5

def test_courses_pagination(client):
    # Create 15 courses
    for i in range(15):
        r = client.post("/api/courses/", json={"code": f"C{i}", "title": f"Course {i}"})
        assert r.status_code == 201

    r = client.get("/api/courses/?limit=7&offset=7")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 7

def test_availabilities_pagination(client, user_factory):
    user = user_factory()
    # Create 12 availabilities for the user
    for i in range(12):
        r = client.post("/api/availabilities/", json={
            "user_id": user["id"],
            "weekday": i % 7,
            "start_min": 60 * ((i % 8) + 1),
            "end_min": 60 * ((i % 8) + 2),
        })
        assert r.status_code == 201

    r = client.get(f"/api/availabilities/?user_id={user['id']}&limit=5&offset=5")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 5

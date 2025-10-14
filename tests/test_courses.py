import pytest

@pytest.mark.asyncio
async def test_course_crud(asgi_client):
    # Create
    resp = await asgi_client.post("/api/courses/", json={"code": "cs101", "title": "Intro CS"})
    assert resp.status_code == 201, resp.text
    c = resp.json()
    cid = c["id"]
    assert c["code"] == "CS101"  # normalized to uppercase

    # List
    resp = await asgi_client.get("/api/courses/")
    assert resp.status_code == 200
    courses = resp.json()
    assert any(x["id"] == cid for x in courses)

    # Get by id
    resp = await asgi_client.get(f"/api/courses/{cid}")
    assert resp.status_code == 200
    one = resp.json()
    assert one["title"] == "Intro CS"

    # Patch
    resp = await asgi_client.patch(f"/api/courses/{cid}", json={"title": "Intro to CS"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Intro to CS"

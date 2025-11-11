import pytest
from app.core.config import settings


def test_stats_requires_api_key_when_enabled(client, monkeypatch):
    # Turn on gating
    monkeypatch.setattr(settings, "REQUIRE_API_KEY", True, raising=False)
    monkeypatch.setattr(settings, "API_KEY", "secret123", raising=False)

    # No key -> 401
    resp = client.get("/api/stats/overview")
    assert resp.status_code == 401

    # Wrong key -> 401
    resp = client.get("/api/stats/overview", headers={"X-API-Key": "nope"})
    assert resp.status_code == 401

    # Correct key -> 200
    resp = client.get("/api/stats/overview", headers={"X-API-Key": "secret123"})
    assert resp.status_code == 200


def test_exports_require_api_key_when_enabled(client, monkeypatch):
    # Gating on
    monkeypatch.setattr(settings, "REQUIRE_API_KEY", True, raising=False)
    monkeypatch.setattr(settings, "API_KEY", "secret123", raising=False)

    url = "/api/exports/courses/1/groups.csv"

    # No key -> 401
    resp = client.get(url)
    assert resp.status_code == 401

    # Correct key -> not 401 (could be 200 or 404 depending on data)
    resp = client.get(url, headers={"X-API-Key": "secret123"})
    assert resp.status_code != 401

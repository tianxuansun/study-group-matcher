# Study Group Matcher

A clean, well-tested FastAPI microservice that forms small, stable study groups from student availability — with course enrollments, matching, and membership management.

[![Tests](https://github.com/tianxuansun/study-group-matcher/actions/workflows/ci.yml/badge.svg)](./actions) <!-- keep or remove if you add CI -->

##  What this project shows
- **Production-style FastAPI**: modular routers, strict schemas, validation, and error handling.
- **Relational modeling with SQLAlchemy**: Users, Courses, Enrollments, Groups, Memberships.
- **A deterministic matching algorithm** with realistic constraints (time overlap, group size).
- **Practical API design**: pagination with `X-Total-Count`, filtering, and idempotent-ish apply flow.
- **Comprehensive tests**: async tests cover CRUD, matching (by users and by course), filters, error paths.

---

##  Tech stack
- **Python 3.10 • FastAPI • Pydantic v2 • SQLAlchemy 2.x**
- **SQLite** (local/dev; swap for Postgres in prod)
- **pytest + httpx (async)** for tests & coverage

---

##  Quick start

```bash
git clone https://github.com/tianxuansun/study-group-matcher.git
cd study-group-matcher
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

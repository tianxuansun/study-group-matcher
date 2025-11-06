# Study Group Matcher

A clean, well-tested FastAPI microservice that I built to form small, stable study groups from student availability — with course enrollments, matching, stats, and CSV exports.

[![CI](https://github.com/tianxuansun/study-group-matcher/actions/workflows/ci.yml/badge.svg)](https://github.com/tianxuansun/study-group-matcher/actions)

---

## What this project shows

- **Production-style FastAPI**: modular routers, strict Pydantic v2 schemas, validation, and consistent error handling.
- **Relational modeling (SQLAlchemy 2.x)**: Users, Courses, Enrollments, Groups, Memberships.
- **Deterministic matching** with realistic constraints (time overlap, fixed group sizes, leftovers handling).
- **Practical API design**: `limit/offset` + `X-Total-Count`, filters, and a preview → apply matching flow.
- **Comprehensive tests**: async pytest/httpx suite; CI on GitHub Actions.
- **Container-ready**: Dockerfile + entrypoint run Alembic migrations then uvicorn.

---

## Tech stack

- **Python 3.10 • FastAPI • Pydantic v2 • SQLAlchemy 2.x**
- **SQLite** for local/dev (swap to Postgres in production)
- **pytest + httpx** for async tests & coverage
- **Docker** for reproducible builds

---

## Quick start (local)

```bash
git clone https://github.com/tianxuansun/study-group-matcher.git
cd study-group-matcher

python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

pip install -r requirements.txt

# Run API
uvicorn app.main:app --reload

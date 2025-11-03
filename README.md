# Study Group Matcher

A clean, well-tested FastAPI microservice that I built to form small, stable study groups from student availability — with course enrollments, matching, stats, and CSV exports.

[![CI](https://github.com/tianxuansun/study-group-matcher/actions/workflows/ci.yml/badge.svg)](https://github.com/tianxuansun/study-group-matcher/actions)

---

## What this project shows

- **Production-style FastAPI**: modular routers, strict Pydantic v2 schemas, validation, and consistent error handling.  
- **Relational modeling (SQLAlchemy 2.x)**: Users, Courses, Enrollments, Groups, Memberships.  
- **Deterministic matching** with realistic constraints (time overlap & fixed group sizes).  
- **Practical API design**: pagination via `limit/offset` + `X-Total-Count`, filtering, and an idempotent-ish “preview → apply” flow.  
- **Comprehensive async tests** with pytest/httpx; CI runs on GitHub Actions.

---

## Tech stack

- **Python 3.10 • FastAPI • Pydantic v2 • SQLAlchemy 2.x**  
- **SQLite** for local/dev (swap for Postgres in prod)  
- **pytest + httpx (async)** for tests & coverage  
- **Docker** image build

---

## Quick start (local)

```bash
git clone https://github.com/tianxuansun/study-group-matcher.git
cd study-group-matcher
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
## Deploy

- **Infra**: ECS Fargate + ALB + RDS (Terraform in `infra/terraform/`), logs & metrics in CloudWatch, alarms for ALB 5xx and p95 latency.
- **CI**: Tests on PR/merge (`ci.yml`).
- **CD**: Build & push to ECR, deploy to ECS on push to `main` (`deploy.yml`).
- **ADR**: [docs/adr/0001-deploy-choice.md](docs/adr/0001-deploy-choice.md)

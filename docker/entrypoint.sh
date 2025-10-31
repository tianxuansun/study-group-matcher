#!/usr/bin/env bash
set -euo pipefail

# Respect DATABASE_URL if provided (Dockerfile sets a default)
: "${DATABASE_URL:=sqlite:////data/dev.db}"
export DATABASE_URL

# Run migrations before starting the API
alembic upgrade head || { echo "Alembic migration failed"; exit 1; }

# Start FastAPI
exec uvicorn app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"

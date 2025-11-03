#!/usr/bin/env bash
set -euo pipefail

# If using Postgres, wait a bit for DB to be reachable (best-effort)
if [[ "${DATABASE_URL:-}" == postgresql* ]]; then
  echo "[entrypoint] Waiting for database..."
  python - <<'PY'
import os, time, sys
from sqlalchemy import create_engine
url = os.environ.get("DATABASE_URL")
eng = create_engine(url, pool_pre_ping=True)
for i in range(30):
    try:
        with eng.connect() as c:
            c.execute("SELECT 1")
        print("[entrypoint] DB is up")
        sys.exit(0)
    except Exception as e:
        print("[entrypoint] DB not up yet...", e)
        time.sleep(2)
sys.exit(1)
PY
fi

# Run migrations
alembic upgrade head

# Start API
exec uvicorn app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"

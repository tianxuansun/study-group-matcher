#!/usr/bin/env bash
set -e

echo "📦 Container starting for: ${APP_NAME:-Study Group Matcher}"

# Ensure /data exists (volume mount)
mkdir -p /data

# Print DB URL for sanity
echo "Using DATABASE_URL=${DATABASE_URL}"

# Initialize DB schema
echo "🔧 Initializing DB schema..."
python -m app.db.init_db

# Optional seeding
if [ "${SEED}" = "1" ]; then
  echo "🌱 Seeding demo data..."
  python -m scripts.seed || true
fi

echo "🚀 Starting API..."
exec python -m uvicorn app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"

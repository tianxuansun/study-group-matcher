FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

# Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY scripts ./scripts

# Copy Alembic config (created by `alembic init`)
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

# Copy entrypoint
COPY docker/entrypoint.sh /entrypoint.sh

# Default envs (overridable)
ENV APP_NAME="Study Group Matcher"
ENV DATABASE_URL="sqlite:////data/dev.db"
ENV HOST="0.0.0.0"
ENV PORT="8000"

# Persist SQLite db
RUN mkdir -p /data

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

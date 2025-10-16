FROM python:3.10-slim

WORKDIR /app

# System deps (optional build tools can be added if needed later)
RUN pip install --no-cache-dir --upgrade pip

# Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY scripts ./scripts
COPY docker/entrypoint.sh /entrypoint.sh

# Env defaults for runtime (overridden by .env.docker)
ENV APP_NAME="Study Group Matcher"
ENV DATABASE_URL="sqlite:////data/dev.db"
ENV HOST="0.0.0.0"
ENV PORT="8000"

# Create /data for the SQLite file (volume will mount here)
RUN mkdir -p /data

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

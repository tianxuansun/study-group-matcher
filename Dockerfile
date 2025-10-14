FROM python:3.10-slim

WORKDIR /app

# System deps (optional: build-essential if you add heavy libs later)
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app ./app
COPY .env.example ./.env.example

# Default env; you can override via --env-file .env
ENV DATABASE_URL=sqlite:///./dev.db
ENV APP_NAME="Study Group Matcher"

EXPOSE 8000

# Run the API
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

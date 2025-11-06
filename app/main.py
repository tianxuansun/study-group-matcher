from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.observability import init_observability

app = FastAPI(title=settings.APP_NAME)

# Structured logs + latency metrics (no-op metrics if EMF lib is missing)
init_observability(app)


@app.get("/healthz", tags=["Health"])
def healthz():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api")

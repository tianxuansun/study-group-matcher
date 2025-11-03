from fastapi import FastAPI, Request
from app.api.router import api_router
import logging, os, time

try:
    from pythonjsonlogger import jsonlogger
except Exception:
    jsonlogger = None

def _enable_json_logs():
    if os.getenv("JSON_LOGS") == "1" and jsonlogger is not None:
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
        handler.setFormatter(formatter)
        root = logging.getLogger()
        root.handlers = [handler]
        root.setLevel(logging.INFO)

_enable_json_logs()

app = FastAPI(title="Study Group Matcher")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    dt_ms = int((time.perf_counter() - t0) * 1000)
    logging.getLogger("request").info(
        "req",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": dt_ms,
        },
    )
    return response

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

app.include_router(api_router, prefix="/api")

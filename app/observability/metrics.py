import logging
import time
from typing import Callable, Awaitable

from fastapi import FastAPI, Request

logger = logging.getLogger("sgm")


# Optional AWS Embedded Metrics support.
# If the library isn't installed, we fall back to a no-op wrapper so local/dev still works.
def _noop_metric_scope(fn: Callable[..., Awaitable]):
    async def wrapper(*args, **kwargs):
        class DummyMetrics:
            def set_namespace(self, *a, **k): ...
            def set_dimensions(self, *a, **k): ...
            def put_metric(self, *a, **k): ...
            def set_property(self, *a, **k): ...

        # inject a dummy "metrics" kwarg like aws_embedded_metrics would
        kwargs.setdefault("metrics", DummyMetrics())
        return await fn(*args, **kwargs)

    return wrapper


try:
    from aws_embedded_metrics import metric_scope as _real_metric_scope  # type: ignore

    metric_scope = _real_metric_scope  # pragma: no cover
except Exception:  # library not installed or misconfigured
    metric_scope = _noop_metric_scope


def init_logging() -> None:
    # Simple key=value style; friendly to CloudWatch log insights.
    logging.basicConfig(
        level=logging.INFO,
        format='ts=%(asctime)s level=%(levelname)s logger=%(name)s msg="%(message)s"',
    )


def init_observability(app: FastAPI, service_name: str = "study-group-matcher") -> None:
    """
    Attach a lightweight metrics + logging middleware.

    - Always logs one line per request.
    - If aws-embedded-metrics is installed, also emits EMF metrics (p95-capable).
    """
    init_logging()

    @app.middleware("http")
    @metric_scope
    async def metrics_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable],
        metrics=None,
    ):
        start = time.perf_counter()
        path = request.url.path
        method = request.method

        # configure EMF if available
        if metrics is not None:
            metrics.set_namespace("SGMApp")
            metrics.set_dimensions({"Service": service_name, "Route": path, "Method": method})

        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        except Exception:
            logger.exception(f"unhandled_error path={path} method={method}")
            raise
        finally:
            dur_ms = (time.perf_counter() - start) * 1000.0

            if metrics is not None:
                metrics.put_metric("RequestLatencyMs", dur_ms, "Milliseconds")
                metrics.put_metric("RequestCount", 1, "Count")
                metrics.set_property("status", status)

            logger.info(
                f"request_done path={path} method={method} status={status} dur_ms={dur_ms:.2f}"
            )

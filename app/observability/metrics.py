import time
import logging
from typing import Callable
from fastapi import FastAPI, Request
from aws_embedded_metrics import metric_scope

logger = logging.getLogger("sgm")

def init_logging():
    # Basic JSON-ish structure using standard logging (CloudWatch can parse key=value pairs)
    logging.basicConfig(
        level=logging.INFO,
        format='msg="%(message)s" level=%(levelname)s ts=%(asctime)s logger=%(name)s',
    )

def init_observability(app: FastAPI, service_name: str = "study-group-matcher"):
    init_logging()

    @app.middleware("http")
    @metric_scope
    async def metrics_middleware(request: Request, call_next: Callable, metrics=None):
        start = time.perf_counter()
        path = request.url.path
        method = request.method

        # Configure CloudWatch Embedded Metrics Format
        metrics.set_namespace("SGMApp")
        metrics.set_dimensions({"Service": service_name, "Route": path, "Method": method})

        try:
            response = await call_next(request)
            status = response.status_code
            return response
        except Exception as e:
            status = 500
            logger.exception(f"unhandled_error path={path} method={method}")
            raise
        finally:
            dur_ms = (time.perf_counter() - start) * 1000.0
            # Emit one datapoint per request. CloudWatch can compute p95 on this metric.
            metrics.put_metric("RequestLatencyMs", dur_ms, "Milliseconds")
            metrics.put_metric("RequestCount", 1, "Count")
            metrics.set_property("status", status)

            # Also log a structured line to stdout
            logger.info(f'request_done path="{path}" method={method} status={status} dur_ms={dur_ms:.2f}')

from typing import Generator, Optional
from hmac import compare_digest

from fastapi import Header, HTTPException

from app.db.session import SessionLocal
from app.core.config import settings


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_api_key(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")
) -> None:
    """
    Optional API key gating for write endpoints.

    Controlled via env:
      REQUIRE_API_KEY=true
      API_KEY=<secret>

    When REQUIRE_API_KEY is false (default), this is a no-op.
    """
    require = getattr(settings, "REQUIRE_API_KEY", False)
    configured = getattr(settings, "API_KEY", None)

    if not require:
        return

    if not x_api_key or not configured or not compare_digest(x_api_key, configured):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

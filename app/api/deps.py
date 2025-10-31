from typing import Generator, Optional
from fastapi import HTTPException, Header
from hmac import compare_digest

from app.db.session import SessionLocal
from app.core.config import settings

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")):
    """
    Optional API-key gating for write endpoints. Controlled by env:
      REQUIRE_API_KEY=true
      API_KEY=<secret>
    """
    if not settings.REQUIRE_API_KEY:
        return
    if not x_api_key or not settings.API_KEY or not compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

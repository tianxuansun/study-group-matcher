from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api.deps import get_db

router = APIRouter()

@router.get("/live")
def live():
    return {"status": "ok"}

@router.get("/ready")
def ready(db: Session = Depends(get_db)):
    # DB ping to confirm connectivity
    db.execute(text("SELECT 1"))
    return {"status": "ok"}

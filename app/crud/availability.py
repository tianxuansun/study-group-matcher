from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.availability import Availability
from app.schemas.availability import AvailabilityCreate, AvailabilityUpdate

def get(db: Session, availability_id: int) -> Optional[Availability]:
    return db.get(Availability, availability_id)

def get_multi(db: Session, skip: int = 0, limit: int = 50, user_id: Optional[int] = None) -> List[Availability]:
    stmt = select(Availability)
    if user_id is not None:
        stmt = stmt.where(Availability.user_id == user_id)
    return db.scalars(stmt.offset(skip).limit(limit)).all()

def create(db: Session, obj_in: AvailabilityCreate) -> Availability:
    obj = Availability(
        user_id=obj_in.user_id,
        weekday=obj_in.weekday,
        start_min=obj_in.start_min,
        end_min=obj_in.end_min,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update(db: Session, db_obj: Availability, obj_in: AvailabilityUpdate) -> Availability:
    data = obj_in.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(db_obj, k, v)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, availability_id: int) -> None:
    obj = get(db, availability_id)
    if obj:
        db.delete(obj)
        db.commit()
def get_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(Availability)
        .filter(Availability.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
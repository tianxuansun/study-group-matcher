from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.errors import not_found
from app.schemas.availability import AvailabilityCreate, AvailabilityUpdate, AvailabilityRead
from app.crud import availability as avail_crud
from app.crud import user as user_crud

router = APIRouter()

@router.get("/", response_model=List[AvailabilityRead])
def list_availabilities(
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    limit = min(max(limit, 1), 100)
    return avail_crud.get_multi(db, skip=skip, limit=limit, user_id=user_id)

@router.post("/", response_model=AvailabilityRead, status_code=status.HTTP_201_CREATED)
def create_availability(payload: AvailabilityCreate, db: Session = Depends(get_db)):
    # ensure user exists
    if not user_crud.get(db, payload.user_id):
        not_found(f"User {payload.user_id} not found")
    return avail_crud.create(db, payload)

@router.get("/{availability_id}", response_model=AvailabilityRead)
def get_availability(availability_id: int, db: Session = Depends(get_db)):
    obj = avail_crud.get(db, availability_id)
    if not obj:
        not_found(f"Availability {availability_id} not found")
    return obj

@router.patch("/{availability_id}", response_model=AvailabilityRead)
def update_availability(availability_id: int, payload: AvailabilityUpdate, db: Session = Depends(get_db)):
    obj = avail_crud.get(db, availability_id)
    if not obj:
        not_found(f"Availability {availability_id} not found")
    return avail_crud.update(db, obj, payload)

@router.delete("/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_availability(availability_id: int, db: Session = Depends(get_db)):
    obj = avail_crud.get(db, availability_id)
    if not obj:
        not_found(f"Availability {availability_id} not found")
    avail_crud.remove(db, availability_id)
    return None

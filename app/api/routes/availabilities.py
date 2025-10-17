from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db
from app.api.errors import not_found
from app.schemas.availability import AvailabilityCreate, AvailabilityUpdate, AvailabilityRead
from app.crud import availability as availability_crud

router = APIRouter()

@router.get("/", response_model=List[AvailabilityRead])
def list_availabilities(
    user_id: Optional[int] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if user_id is not None:
        return availability_crud.get_by_user(db, user_id=user_id, skip=offset, limit=limit)
    return availability_crud.get_multi(db, skip=offset, limit=limit)

@router.post("/", response_model=AvailabilityRead, status_code=status.HTTP_201_CREATED)
def create_availability(payload: AvailabilityCreate, db: Session = Depends(get_db)):
    return availability_crud.create(db, payload)

@router.get("/{availability_id}", response_model=AvailabilityRead)
def get_availability(availability_id: int, db: Session = Depends(get_db)):
    obj = availability_crud.get(db, availability_id)  # positional
    if not obj:
        not_found("Availability not found.")
    return obj

@router.patch("/{availability_id}", response_model=AvailabilityRead)
def update_availability(availability_id: int, payload: AvailabilityUpdate, db: Session = Depends(get_db)):
    obj = availability_crud.get(db, availability_id)  # positional
    if not obj:
        not_found("Availability not found.")
    return availability_crud.update(db, db_obj=obj, obj_in=payload)

@router.delete("/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_availability(availability_id: int, db: Session = Depends(get_db)):
    obj = availability_crud.get(db, availability_id)  # positional
    if not obj:
        not_found("Availability not found.")
    availability_crud.remove(db, availability_id)  # positional
    return


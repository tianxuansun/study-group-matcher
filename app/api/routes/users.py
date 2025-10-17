from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.api.errors import conflict, not_found
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.crud import user as user_crud

router = APIRouter()

@router.get("/", response_model=List[UserRead])
def list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),   # was 20 -> now 100
    db: Session = Depends(get_db),
):
    return user_crud.get_multi(db, skip=offset, limit=limit)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_crud.create(db, payload)
    except ValueError as e:
        if str(e) == "email_conflict":
            conflict("Email already exists.")
        raise

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    obj = user_crud.get(db, user_id)  # positional
    if not obj:
        not_found("User not found.")
    return obj

@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    obj = user_crud.get(db, user_id)  # positional
    if not obj:
        not_found("User not found.")
    return user_crud.update(db, db_obj=obj, obj_in=payload)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    obj = user_crud.get(db, user_id)  # positional
    if not obj:
        not_found("User not found.")
    user_crud.remove(db, user_id)  # positional
    return

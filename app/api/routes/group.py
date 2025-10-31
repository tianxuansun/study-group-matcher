from typing import List
from fastapi import APIRouter, Depends, status, Query
from fastapi import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.errors import not_found, conflict
from app.schemas.group import GroupCreate, GroupUpdate, GroupRead
from app.crud import group as group_crud
from app.api.deps import require_api_key

router = APIRouter()

@router.get("/", response_model=List[GroupRead])
def list_groups(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    name_prefix: str | None = Query(None, min_length=1),
    course_id: int | None = Query(None, ge=1),
    db: Session = Depends(get_db),
    response: Response = None,  # NEW
):
    total = group_crud.count(db, name_prefix=name_prefix, course_id=course_id)
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
    return group_crud.get_multi(db, skip=offset, limit=limit, name_prefix=name_prefix, course_id=course_id)

@router.post("/", response_model=GroupRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_api_key)])
def create_group(payload: GroupCreate, db: Session = Depends(get_db)):
    try:
        return group_crud.create(db, payload)
    except ValueError as e:
        if str(e) == "course_not_found":
            not_found("Course not found.")
        raise

@router.get("/{group_id}", response_model=GroupRead)
def get_group(group_id: int, db: Session = Depends(get_db)):
    obj = group_crud.get(db, group_id)
    if not obj:
        not_found("Group not found.")
    return obj

@router.patch("/{group_id}", response_model=GroupRead,
              dependencies=[Depends(require_api_key)])
def update_group(group_id: int, payload: GroupUpdate, db: Session = Depends(get_db)):
    obj = group_crud.get(db, group_id)
    if not obj:
        not_found("Group not found.")
    try:
        return group_crud.update(db, db_obj=obj, obj_in=payload)
    except ValueError as e:
        if str(e) == "course_not_found":
            not_found("Course not found.")
        raise

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_api_key)])
def delete_group(group_id: int, db: Session = Depends(get_db)):
    obj = group_crud.get(db, group_id)
    if not obj:
        not_found("Group not found.")
    group_crud.remove(db, group_id)
    return

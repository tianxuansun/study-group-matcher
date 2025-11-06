from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.api.errors import not_found
from app.crud import group as group_crud
from app.schemas.group import GroupCreate, GroupRead, GroupUpdate

router = APIRouter()


@router.get("/", response_model=List[GroupRead])
def list_groups(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    name_prefix: Optional[str] = Query(None, min_length=1),
    course_id: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
    response: Response = None,
):
    total = group_crud.count(
        db, name_prefix=name_prefix, course_id=course_id
    )
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
    return group_crud.get_multi(
        db,
        skip=offset,
        limit=limit,
        name_prefix=name_prefix,
        course_id=course_id,
    )


@router.post("/", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
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


@router.patch("/{group_id}", response_model=GroupRead)
def update_group(
    group_id: int,
    payload: GroupUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
    obj = group_crud.get(db, group_id)
    if not obj:
        not_found("Group not found.")
    try:
        return group_crud.update(db, db_obj=obj, obj_in=payload)
    except ValueError as e:
        if str(e) == "course_not_found":
            not_found("Course not found.")
        raise


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
    obj = group_crud.get(db, group_id)
    if not obj:
        not_found("Group not found.")
    group_crud.remove(db, group_id)
    return

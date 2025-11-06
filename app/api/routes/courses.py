from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.api.errors import conflict, not_found
from app.crud import course as course_crud
from app.schemas.course import CourseCreate, CourseRead, CourseUpdate

router = APIRouter()


@router.get("/", response_model=List[CourseRead])
def list_courses(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return course_crud.get_multi(db, skip=offset, limit=limit)


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
    try:
        return course_crud.create(db, payload)
    except ValueError as e:
        if str(e) == "code_conflict":
            conflict("Course code already exists.")
        raise


@router.get("/{course_id}", response_model=CourseRead)
def get_course(course_id: int, db: Session = Depends(get_db)):
    obj = course_crud.get(db, course_id)
    if not obj:
        not_found("Course not found.")
    return obj


@router.patch("/{course_id}", response_model=CourseRead)
def update_course(
    course_id: int,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
    obj = course_crud.get(db, course_id)
    if not obj:
        not_found("Course not found.")
    return course_crud.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
    obj = course_crud.get(db, course_id)
    if not obj:
        not_found("Course not found.")
    course_crud.remove(db, course_id)
    return

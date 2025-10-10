from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.api.errors import conflict, not_found
from app.schemas.course import CourseCreate, CourseUpdate, CourseRead
from app.crud import course as course_crud

router = APIRouter()

@router.get("/", response_model=List[CourseRead])
def list_courses(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    limit = min(max(limit, 1), 100)
    return course_crud.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
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
        not_found(f"Course {course_id} not found")
    return obj

@router.patch("/{course_id}", response_model=CourseRead)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db)):
    obj = course_crud.get(db, course_id)
    if not obj:
        not_found(f"Course {course_id} not found")
    try:
        return course_crud.update(db, obj, payload)
    except ValueError as e:
        if str(e) == "code_conflict":
            conflict("Course code already exists.")
        raise

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    obj = course_crud.get(db, course_id)
    if not obj:
        not_found(f"Course {course_id} not found")
    course_crud.remove(db, course_id)
    return None

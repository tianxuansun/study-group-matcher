from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.errors import not_found, conflict
from app.schemas.enrollment import EnrollmentCreate, EnrollmentRead
from app.crud import enrollment as crud

router = APIRouter()

def _bounded_limit(limit: int) -> int:
    return min(max(limit, 1), 100)

@router.post("/", response_model=EnrollmentRead, status_code=status.HTTP_201_CREATED)
def enroll(payload: EnrollmentCreate, db: Session = Depends(get_db)):
    try:
        obj = crud.create(db, payload.user_id, payload.course_id)
    except ValueError as e:
        if str(e) == "not_found_user":
            not_found(f"User {payload.user_id} not found")
        if str(e) == "not_found_course":
            not_found(f"Course {payload.course_id} not found")
        if str(e) == "conflict":
            conflict("Enrollment already exists")
        raise
    return EnrollmentRead(user_id=obj.user_id, course_id=obj.course_id)

@router.get("/", response_model=List[EnrollmentRead], status_code=status.HTTP_200_OK)
def list_enrollments(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    course_id: Optional[int] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    limit = _bounded_limit(limit)
    if user_id is not None and course_id is not None:
        # narrowest scope: intersection
        rows, total = [], 0
        if crud.exists(db, user_id, course_id):
            rows = [EnrollmentRead(user_id=user_id, course_id=course_id)]
            total = 1
    elif user_id is not None:
        rows, total = crud.list_for_user(db, user_id, limit, offset)
        rows = [EnrollmentRead(user_id=r.user_id, course_id=r.course_id) for r in rows]
    elif course_id is not None:
        rows, total = crud.list_for_course(db, course_id, limit, offset)
        rows = [EnrollmentRead(user_id=r.user_id, course_id=r.course_id) for r in rows]
    else:
        rows, total = crud.list_all(db, limit, offset)
        rows = [EnrollmentRead(user_id=r.user_id, course_id=r.course_id) for r in rows]
    resp = JSONResponse(content=[r.model_dump() for r in rows])
    resp.headers["X-Total-Count"] = str(total)
    return resp

@router.delete("/{user_id}/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def unenroll(user_id: int, course_id: int, db: Session = Depends(get_db)):
    ok = crud.remove(db, user_id, course_id)
    if not ok:
        not_found(f"Enrollment user={user_id}, course={course_id} not found")
    return None

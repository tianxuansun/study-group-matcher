from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.enrollment import Enrollment
from app.models.user import User
from app.models.course import Course

def exists(db: Session, user_id: int, course_id: int) -> bool:
    stmt = select(func.count()).select_from(Enrollment).where(
        Enrollment.user_id == user_id, Enrollment.course_id == course_id
    )
    return db.scalar(stmt) > 0

def create(db: Session, user_id: int, course_id: int) -> Enrollment:
    # verify user & course exist
    if db.get(User, user_id) is None:
        raise ValueError("not_found_user")
    if db.get(Course, course_id) is None:
        raise ValueError("not_found_course")
    if exists(db, user_id, course_id):
        raise ValueError("conflict")
    obj = Enrollment(user_id=user_id, course_id=course_id)
    db.add(obj)
    db.commit()
    return obj

def remove(db: Session, user_id: int, course_id: int) -> bool:
    # Session.get for composite PK expects a tuple in primary key order
    obj = db.get(Enrollment, (user_id, course_id))
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def list_for_user(db: Session, user_id: int, limit: int, offset: int) -> Tuple[List[Enrollment], int]:
    total = db.scalar(select(func.count()).select_from(Enrollment).where(Enrollment.user_id == user_id)) or 0
    rows = db.scalars(
        select(Enrollment).where(Enrollment.user_id == user_id).offset(offset).limit(limit)
    ).all()
    return rows, total

def list_for_course(db: Session, course_id: int, limit: int, offset: int) -> Tuple[List[Enrollment], int]:
    total = db.scalar(select(func.count()).select_from(Enrollment).where(Enrollment.course_id == course_id)) or 0
    rows = db.scalars(
        select(Enrollment).where(Enrollment.course_id == course_id).offset(offset).limit(limit)
    ).all()
    return rows, total

def list_all(db: Session, limit: int, offset: int) -> Tuple[List[Enrollment], int]:
    total = db.scalar(select(func.count()).select_from(Enrollment)) or 0
    rows = db.scalars(select(Enrollment).offset(offset).limit(limit)).all()
    return rows, total

def user_ids_for_course(db: Session, course_id: int) -> List[int]:
    return [row.user_id for row in db.scalars(select(Enrollment).where(Enrollment.course_id == course_id)).all()]

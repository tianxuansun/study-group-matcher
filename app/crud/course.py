from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate

def get(db: Session, course_id: int) -> Course | None:
    return db.get(Course, course_id)

def get_by_code(db: Session, code: str) -> Course | None:
    # code should already be uppercase by schema validator, but normalize anyway
    code_up = code.strip().upper()
    return db.scalar(select(Course).where(Course.code == code_up))

def get_multi(db: Session, skip: int = 0, limit: int = 50) -> list[Course]:
    return db.scalars(select(Course).offset(skip).limit(limit)).all()

def create(db: Session, obj_in: CourseCreate) -> Course:
    code_up = obj_in.code.strip().upper()
    if get_by_code(db, code_up):
        raise ValueError("code_conflict")
    course = Course(code=code_up, title=obj_in.title)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

def update(db: Session, db_obj: Course, obj_in: CourseUpdate) -> Course:
    data = obj_in.model_dump(exclude_unset=True)
    if "code" in data and data["code"]:
        new_code = data["code"].strip().upper()
        existing = get_by_code(db, new_code)
        if existing and existing.id != db_obj.id:
            raise ValueError("code_conflict")
        db_obj.code = new_code
    if "title" in data and data["title"] is not None:
        db_obj.title = data["title"]
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, course_id: int) -> None:
    obj = get(db, course_id)
    if obj:
        db.delete(obj)
        db.commit()

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.group import Group
from app.models.course import Course
from app.schemas.group import GroupCreate, GroupUpdate

def get(db: Session, id: int) -> Group | None:
    return db.get(Group, id)

def get_multi(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name_prefix: str | None = None,
    course_id: int | None = None,
) -> list[Group]:
    stmt = select(Group).order_by(Group.id.asc())
    if name_prefix:
        stmt = stmt.where(Group.name.like(f"{name_prefix}%"))
    if course_id is not None:
        stmt = stmt.where(Group.course_id == course_id)
    stmt = stmt.offset(skip).limit(limit)
    return db.scalars(stmt).all()


def create(db: Session, obj_in: GroupCreate) -> Group:
    if obj_in.course_id is not None:
        if db.get(Course, obj_in.course_id) is None:
            raise ValueError("course_not_found")
    obj = Group(name=obj_in.name, course_id=obj_in.course_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update(db: Session, db_obj: Group, obj_in: GroupUpdate) -> Group:
    data = obj_in.model_dump(exclude_unset=True)
    if "course_id" in data and data["course_id"] is not None:
        if db.get(Course, data["course_id"]) is None:
            raise ValueError("course_not_found")
    for k, v in data.items():
        setattr(db_obj, k, v)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, id: int) -> None:
    obj = db.get(Group, id)
    if obj:
        db.delete(obj)
        db.commit()

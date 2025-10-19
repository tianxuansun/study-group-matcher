from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.models.membership import Membership
from app.models.user import User
from app.models.group import Group
from app.schemas.membership import MembershipCreate, MembershipUpdate

def get(db: Session, id: int) -> Membership | None:
    return db.get(Membership, id)

def get_multi(db: Session, skip: int = 0, limit: int = 100) -> list[Membership]:
    stmt = select(Membership).order_by(Membership.id.asc()).offset(skip).limit(limit)
    return db.scalars(stmt).all()

def get_by_user_group(db: Session, user_id: int, group_id: int) -> Membership | None:
    stmt = select(Membership).where(and_(Membership.user_id == user_id, Membership.group_id == group_id))
    return db.scalar(stmt)

def create(db: Session, obj_in: MembershipCreate) -> Membership:
    if db.get(User, obj_in.user_id) is None:
        raise ValueError("user_not_found")
    if db.get(Group, obj_in.group_id) is None:
        raise ValueError("group_not_found")
    if get_by_user_group(db, obj_in.user_id, obj_in.group_id):
        raise ValueError("membership_conflict")
    obj = Membership(user_id=obj_in.user_id, group_id=obj_in.group_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update(db: Session, db_obj: Membership, obj_in: MembershipUpdate) -> Membership:
    data = obj_in.model_dump(exclude_unset=True)
    # avoid creating duplicates on update
    new_user_id = data.get("user_id", db_obj.user_id)
    new_group_id = data.get("group_id", db_obj.group_id)
    if db.get(User, new_user_id) is None:
        raise ValueError("user_not_found")
    if db.get(Group, new_group_id) is None:
        raise ValueError("group_not_found")
    existing = get_by_user_group(db, new_user_id, new_group_id)
    if existing and existing.id != db_obj.id:
        raise ValueError("membership_conflict")
    db_obj.user_id = new_user_id
    db_obj.group_id = new_group_id
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, id: int) -> None:
    obj = db.get(Membership, id)
    if obj:
        db.delete(obj)
        db.commit()

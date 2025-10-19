from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

def get(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)

def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))

def get_multi(db: Session, skip: int = 0, limit: int = 50) -> list[User]:
    stmt = select(User).order_by(User.id.asc()).offset(skip).limit(limit)
    return db.scalars(stmt).all()


def create(db: Session, obj_in: UserCreate) -> User:
    email = obj_in.email.lower()
    if get_by_email(db, email):
        # let route decide how to surface conflict if you prefer
        raise ValueError("email_conflict")
    user = User(email=email, name=obj_in.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update(db: Session, db_obj: User, obj_in: UserUpdate) -> User:
    data = obj_in.model_dump(exclude_unset=True)
    if "email" in data and data["email"]:
        new_email = data["email"].lower()
        # conflict if email belongs to another user
        existing = get_by_email(db, new_email)
        if existing and existing.id != db_obj.id:
            raise ValueError("email_conflict")
        db_obj.email = new_email
    if "name" in data and data["name"] is not None:
        db_obj.name = data["name"]
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, user_id: int) -> None:
    obj = get(db, user_id)
    if obj:
        db.delete(obj)
        db.commit()

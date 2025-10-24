from typing import List
from fastapi import APIRouter, Depends, status, Query
from fastapi import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.errors import not_found, conflict
from app.schemas.membership import MembershipCreate, MembershipUpdate, MembershipRead
from app.crud import membership as membership_crud

router = APIRouter()

@router.get("/", response_model=List[MembershipRead])
def list_memberships(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: int | None = Query(None, ge=1),
    group_id: int | None = Query(None, ge=1),
    db: Session = Depends(get_db),
    response: Response = None,  # NEW
):
    total = membership_crud.count(db, user_id=user_id, group_id=group_id)
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
    return membership_crud.get_multi(db, skip=offset, limit=limit, user_id=user_id, group_id=group_id)
    
@router.post("/", response_model=MembershipRead, status_code=status.HTTP_201_CREATED)
def create_membership(payload: MembershipCreate, db: Session = Depends(get_db)):
    try:
        return membership_crud.create(db, payload)
    except ValueError as e:
        s = str(e)
        if s == "user_not_found":
            not_found("User not found.")
        elif s == "group_not_found":
            not_found("Group not found.")
        elif s == "membership_conflict":
            conflict("Membership already exists.")
        raise

@router.get("/{membership_id}", response_model=MembershipRead)
def get_membership(membership_id: int, db: Session = Depends(get_db)):
    obj = membership_crud.get(db, membership_id)
    if not obj:
        not_found("Membership not found.")
    return obj

@router.patch("/{membership_id}", response_model=MembershipRead)
def update_membership(membership_id: int, payload: MembershipUpdate, db: Session = Depends(get_db)):
    obj = membership_crud.get(db, membership_id)
    if not obj:
        not_found("Membership not found.")
    try:
        return membership_crud.update(db, db_obj=obj, obj_in=payload)
    except ValueError as e:
        s = str(e)
        if s == "user_not_found":
            not_found("User not found.")
        elif s == "group_not_found":
            not_found("Group not found.")
        elif s == "membership_conflict":
            conflict("Membership already exists.")
        raise

@router.delete("/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_membership(membership_id: int, db: Session = Depends(get_db)):
    obj = membership_crud.get(db, membership_id)
    if not obj:
        not_found("Membership not found.")
    membership_crud.remove(db, membership_id)
    return

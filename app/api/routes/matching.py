from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.errors import not_found, conflict
from app.schemas.matching import MatchInput, MatchPlan
from app.services.matching import preview_plan, apply_plan

router = APIRouter()

@router.post("/preview/", response_model=MatchPlan, status_code=status.HTTP_200_OK)
def preview(payload: MatchInput, db: Session = Depends(get_db)):
    # no DB writes; just compute
    plan = preview_plan(db, payload)
    return plan

@router.post("/apply/", response_model=MatchPlan, status_code=status.HTTP_201_CREATED)
def apply(payload: MatchInput, db: Session = Depends(get_db)):
    # compute first
    plan = preview_plan(db, payload)
    if not plan.groups:
        # if nothing to create, it’s more helpful to 400 than 201
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No viable groups for given parameters.")
    created = apply_plan(db, plan, payload.course_id)
    # return the plan that was applied (client can refetch groups if needed)
    return plan

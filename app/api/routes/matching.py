from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.matching import MatchInput, MatchPlan, MatchCourseInput
from app.services.matching import preview_plan, apply_plan
from app.crud import enrollment as enrollment_crud

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
        raise HTTPException(status_code=400, detail="No viable groups for given parameters.")
    apply_plan(db, plan, payload.course_id, name_prefix=payload.name_prefix)
    # return the plan that was applied (client can refetch groups if needed)
    return plan

@router.post("/preview/by-course/{course_id}/", response_model=MatchPlan, status_code=status.HTTP_200_OK)
def preview_by_course(course_id: int, payload: MatchCourseInput, db: Session = Depends(get_db)):
    user_ids = enrollment_crud.user_ids_for_course(db, course_id)
    if not user_ids:
        raise HTTPException(status_code=404, detail=f"No users enrolled in course {course_id}")
    plan = preview_plan(db, MatchInput(
        user_ids=user_ids,
        group_size=payload.group_size,
        min_overlap_minutes=payload.min_overlap_minutes,
        course_id=course_id,
        allow_partial_last_group=payload.allow_partial_last_group,
        name_prefix=payload.name_prefix,
    ))
    return plan

@router.post("/apply/by-course/{course_id}/", response_model=MatchPlan, status_code=status.HTTP_201_CREATED)
def apply_by_course(course_id: int, payload: MatchCourseInput, db: Session = Depends(get_db)):
    user_ids = enrollment_crud.user_ids_for_course(db, course_id)
    if not user_ids:
        raise HTTPException(status_code=404, detail=f"No users enrolled in course {course_id}")
    plan = preview_plan(db, MatchInput(
        user_ids=user_ids,
        group_size=payload.group_size,
        min_overlap_minutes=payload.min_overlap_minutes,
        course_id=course_id,
        allow_partial_last_group=payload.allow_partial_last_group,
        name_prefix=payload.name_prefix,
    ))
    if not plan.groups:
        raise HTTPException(status_code=400, detail="No viable groups for given parameters.")
    apply_plan(db, plan, course_id, name_prefix=payload.name_prefix)
    return plan

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.api.deps import get_db, require_api_key
from app.models.user import User
from app.models.course import Course
from app.models.group import Group
from app.models.membership import Membership
from app.models.enrollment import Enrollment

router = APIRouter()


@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
    totals = {
        "users": db.scalar(select(func.count()).select_from(User)) or 0,
        "courses": db.scalar(select(func.count()).select_from(Course)) or 0,
        "groups": db.scalar(select(func.count()).select_from(Group)) or 0,
        "memberships": db.scalar(select(func.count()).select_from(Membership)) or 0,
        "enrollments": db.scalar(select(func.count()).select_from(Enrollment)) or 0,
    }

    per_course = []
    courses = db.scalars(select(Course).order_by(Course.id.asc())).all()
    for c in courses:
        enrolled_ids = set(
            db.scalars(
                select(Enrollment.user_id).where(Enrollment.course_id == c.id)
            ).all()
        )
        enrolled = len(enrolled_ids)

        groups_count = (
            db.scalar(
                select(func.count())
                .select_from(Group)
                .where(Group.course_id == c.id)
            )
            or 0
        )

        members_in_groups = (
            db.scalar(
                select(func.count())
                .select_from(Membership)
                .join(Group, Group.id == Membership.group_id)
                .where(Group.course_id == c.id)
            )
            or 0
        )

        avg_group_size = (
            float(members_in_groups) / groups_count if groups_count else 0.0
        )

        member_user_ids = set(
            db.scalars(
                select(Membership.user_id)
                .join(Group, Group.id == Membership.group_id)
                .where(Group.course_id == c.id)
            ).all()
        )
        ungrouped_enrolled = len(enrolled_ids - member_user_ids)

        per_course.append(
            {
                "course_id": c.id,
                "code": c.code,
                "title": c.title,
                "enrolled": enrolled,
                "groups": groups_count,
                "members_in_groups": members_in_groups,
                "avg_group_size": round(avg_group_size, 2),
                "ungrouped_enrolled": ungrouped_enrolled,
            }
        )

    return {"totals": totals, "per_course": per_course}

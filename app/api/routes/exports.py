import csv
import io
from fastapi import APIRouter, Depends
from starlette.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db
from app.api.errors import not_found
from app.models.course import Course
from app.models.group import Group
from app.models.membership import Membership
from app.models.user import User

router = APIRouter()

@router.get("/courses/{course_id}/groups.csv")
def export_course_groups_csv(course_id: int, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course:
        not_found("Course not found.")

    # Group info + roster rows (left join users so empty groups still appear)
    stmt = (
        select(
            Group.id,
            Group.name,
            User.id,
            User.email,
            User.name,
        )
        .join(Membership, Membership.group_id == Group.id, isouter=True)
        .join(User, User.id == Membership.user_id, isouter=True)
        .where(Group.course_id == course_id)
        .order_by(Group.id.asc(), User.id.asc())
    )
    rows = db.execute(stmt).all()

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["group_id", "group_name", "user_id", "user_email", "user_name"])
    for g_id, g_name, u_id, u_email, u_name in rows:
        w.writerow([
            g_id,
            g_name,
            u_id if u_id is not None else "",
            u_email if u_email is not None else "",
            u_name if u_name is not None else "",
        ])

    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="course_{course_id}_groups.csv"'},
    )


@router.get("/groups/{group_id}/roster.csv")
def export_group_roster_csv(group_id: int, db: Session = Depends(get_db)):
    group = db.get(Group, group_id)
    if not group:
        not_found("Group not found.")

    stmt = (
        select(User.id, User.email, User.name)
        .join(Membership, Membership.user_id == User.id)
        .where(Membership.group_id == group_id)
        .order_by(User.id.asc())
    )
    members = db.execute(stmt).all()

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["user_id", "user_email", "user_name"])
    for u_id, u_email, u_name in members:
        w.writerow([u_id, u_email, u_name])

    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="group_{group_id}_roster.csv"'},
    )

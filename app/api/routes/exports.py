import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db, require_api_key
from app.api.errors import not_found
from app.models.course import Course
from app.models.group import Group
from app.models.membership import Membership
from app.models.user import User

router = APIRouter()


@router.get("/courses/{course_id}/groups.csv")
def export_course_groups_csv(
    course_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
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
        w.writerow(
            [
                g_id,
                g_name,
                u_id if u_id is not None else "",
                u_email if u_email is not None else "",
                u_name if u_name is not None else "",
            ]
        )

    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="course_{course_id}_groups.csv"'
        },
    )


@router.get("/groups/{group_id}/roster.csv")
def export_group_roster_csv(
    group_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
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
        headers={
            "Content-Disposition": f'attachment; filename="group_{group_id}_roster.csv"'
        },
    )


WEEKDAY_TO_BYDAY = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


def _hm_from_minutes(total: int) -> tuple[int, int]:
    return total // 60, total % 60


def _ics_header() -> list[str]:
    return [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Study Group Matcher//EN",
    ]


def _ics_footer() -> list[str]:
    return ["END:VCALENDAR"]


def _vevent_for_group(g: Group) -> list[str]:
    if (
        g.meeting_weekday is None
        or g.meeting_start_min is None
        or g.meeting_end_min is None
    ):
        raise ValueError("group_has_no_schedule")

    byday = WEEKDAY_TO_BYDAY[g.meeting_weekday]
    start_h, start_m = _hm_from_minutes(g.meeting_start_min)
    duration_min = int(g.meeting_end_min - g.meeting_start_min)
    if duration_min <= 0:
        raise ValueError("invalid_schedule_duration")

    # Fixed DTSTART; RRULE drives recurrence.
    dtstart = f"20250101T{start_h:02d}{start_m:02d}00"

    now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    uid = f"group-{g.id}@sgm"

    return [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{now}",
        f"SUMMARY:{g.name}",
        f"DTSTART:{dtstart}",
        f"RRULE:FREQ=WEEKLY;BYDAY={byday}",
        f"DURATION:PT{duration_min}M",
        "END:VEVENT",
    ]


@router.get("/groups/{group_id}/schedule.ics")
def export_group_schedule_ics(
    group_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
    group = db.get(Group, group_id)
    if not group:
        not_found("Group not found.")

    try:
        vevent = _vevent_for_group(group)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    lines = _ics_header() + vevent + _ics_footer()
    body = "\r\n".join(lines) + "\r\n"
    return Response(
        content=body,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="group_{group_id}_schedule.ics"'
        },
    )


@router.get("/courses/{course_id}/schedules.ics")
def export_course_schedules_ics(
    course_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
):
    course = db.get(Course, course_id)
    if not course:
        not_found("Course not found.")

    stmt = (
        select(Group)
        .where(Group.course_id == course_id)
        .order_by(Group.id.asc())
    )
    groups = db.scalars(stmt).all()

    vevents: list[str] = []
    for g in groups:
        try:
            vevents += _vevent_for_group(g)
        except ValueError:
            # skip groups without valid schedules
            continue

    if not vevents:
        raise HTTPException(
            status_code=404,
            detail="No scheduled groups for this course.",
        )

    lines = _ics_header() + vevents + _ics_footer()
    body = "\r\n".join(lines) + "\r\n"
    return Response(
        content=body,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="course_{course_id}_schedules.ics"'
        },
    )

import uuid
import pytest

from app.db.session import SessionLocal
from app.models.course import Course
from app.models.group import Group
from app.models.membership import Membership
from app.models.user import User
from app.schemas.matching import MatchPlan, MatchGroup, MatchSlot
from app.services.matching import apply_plan


@pytest.fixture
def db_session(app_with_tmp_db):
    """
    Use the same temporary DB wiring as the rest of the suite.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}@example.com"


def test_apply_plan_persists_schedule(db_session):
    # 1) Create a course; apply_plan expects a valid course_id when provided.
    course = Course(
        code=f"CS-{uuid.uuid4().hex[:6]}",
        title="Test Course",
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)

    # 2) Seed users with unique emails.
    u1 = User(email=_unique_email("u1"), name="User One")
    u2 = User(email=_unique_email("u2"), name="User Two")
    db_session.add_all([u1, u2])
    db_session.commit()
    db_session.refresh(u1)
    db_session.refresh(u2)

    # 3) Build a MatchPlan with one group and a concrete slot.
    slot = MatchSlot(weekday=2, start_min=600, end_min=660)  # Tue 10:00–11:00

    plan = MatchPlan(
        groups=[
            MatchGroup(
                user_ids=[u1.id, u2.id],
                slot=slot,
            )
        ],
        leftovers=[],
        params={
            "group_size": 2,
            "min_overlap_minutes": 60,
            "course_id": course.id,
            "allow_partial_last_group": False,
            "name_prefix": "Auto Group",
            "diagnostics": False,
        },
        debug=None,
    )

    # 4) Apply the plan against that course.
    created_ids = apply_plan(
        db_session,
        plan,
        course_id=course.id,
        name_prefix="Course 1 Group",
    )

    # We expect exactly one group created.
    assert len(created_ids) == 1
    group_id = created_ids[0]

    # 5) Assert schedule + course persisted on the Group.
    grp = db_session.get(Group, group_id)
    assert grp is not None
    assert grp.course_id == course.id
    assert grp.meeting_weekday == slot.weekday
    assert grp.meeting_start_min == slot.start_min
    assert grp.meeting_end_min == slot.end_min

    # 6) Assert memberships created correctly.
    memberships = (
        db_session.query(Membership)
        .filter(Membership.group_id == grp.id)
        .order_by(Membership.user_id)
        .all()
    )
    assert [m.user_id for m in memberships] == [u1.id, u2.id]

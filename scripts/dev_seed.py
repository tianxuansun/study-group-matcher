# scripts/dev_seed.py
# Populate demo data and auto-group them.

from app.db.session import SessionLocal
from app.crud import user as user_crud
from app.crud import enrollment as enroll_crud
from app.crud import course as course_crud
from app.schemas.user import UserCreate
from app.schemas.course import CourseCreate
from app.schemas.matching import MatchInput
from app.services.matching import preview_plan, apply_plan
from app.models.availability import Availability
from sqlalchemy import select

def ensure_user(db, email, name):
    from app.crud.user import get_by_email
    u = get_by_email(db, email)
    if u:
        return u
    return user_crud.create(db, UserCreate(email=email, name=name))

def add_availability(db, user_id, weekday, start_min, end_min):
    # idempotent-ish: skip if identical exists
    exists = db.scalars(
        select(Availability).where(
            Availability.user_id == user_id,
            Availability.weekday == weekday,
            Availability.start_min == start_min,
            Availability.end_min == end_min,
        )
    ).first()
    if exists:
        return
    db.add(Availability(user_id=user_id, weekday=weekday, start_min=start_min, end_min=end_min))
    db.commit()

def main():
    db = SessionLocal()
    try:
        # Course
        course = course_crud.get_by_code(db, "DEMO101") if hasattr(course_crud, "get_by_code") else None
        if not course:
            course = course_crud.create(db, CourseCreate(code="DEMO101", title="Demo Course"))

        # Users
        emails = [f"demo{i}@example.com" for i in range(1, 7)]
        users = [ensure_user(db, e, f"Demo {i+1}") for i, e in enumerate(emails)]

        # Enroll + availability (Wed 14:00-16:00)
        for u in users:
            try:
                enroll_crud.create(db, u.id, course.id)
            except ValueError:
                pass
            add_availability(db, u.id, weekday=2, start_min=14*60, end_min=16*60)

        # Match into groups of 3 with 60-min overlap
        payload = MatchInput(
            user_ids=[u.id for u in users],
            group_size=3,
            min_overlap_minutes=60,
            course_id=course.id,
            allow_partial_last_group=False,
            name_prefix="Demo Group"
        )
        plan = preview_plan(db, payload)
        apply_plan(db, plan, course_id=course.id, name_prefix="Demo Group")

        print("Seed complete. Created course DEMO101, users, enrollments, availabilities, and groups.")
    finally:
        db.close()

if __name__ == "__main__":
    main()

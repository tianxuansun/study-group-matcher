from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint
from app.db.base import Base

# Reuse an existing 'user_courses' Table if already defined (avoids duplicate table errors)
user_courses = Base.metadata.tables.get("user_courses")
if user_courses is None:
    user_courses = Table(
        "user_courses",
        Base.metadata,
        Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True),
        Column("course_id", Integer, ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True, index=True),
        UniqueConstraint("user_id", "course_id", name="uq_user_course"),
    )

# Map the class to that single Table object
class Enrollment(Base):
    __table__ = user_courses
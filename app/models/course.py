from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    code = Column(String(32), nullable=False, unique=True, index=True)  # e.g., CS523
    title = Column(String(200), nullable=False)

    users = relationship("User", secondary="user_courses", back_populates="courses")
    groups = relationship("Group", back_populates="course")
from sqlalchemy import Table, Column, Integer, ForeignKey

user_courses = Table(
    "user_courses",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    meeting_weekday = Column(Integer, nullable=True)
    meeting_start_min = Column(Integer, nullable=True)
    meeting_end_min = Column(Integer, nullable=True)

    course = relationship("Course", back_populates="groups")
    memberships = relationship("Membership", back_populates="group", cascade="all, delete-orphan")
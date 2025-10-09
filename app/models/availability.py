from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Availability(Base):
    __tablename__ = "availabilities"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    weekday = Column(Integer, nullable=False)   # 0=Mon .. 6=Sun
    start_min = Column(Integer, nullable=False) # 0..1440
    end_min = Column(Integer, nullable=False)   # 0..1440, > start_min

    user = relationship("User", back_populates="availabilities")

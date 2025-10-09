from pydantic import BaseModel, Field
from typing import Optional

class GroupBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    course_id: Optional[int] = None

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    course_id: Optional[int] = None

class GroupRead(GroupBase):
    id: int
    model_config = {"from_attributes": True}

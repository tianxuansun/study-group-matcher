from pydantic import BaseModel, Field, field_validator
from typing import Optional

class CourseBase(BaseModel):
    code: str = Field(min_length=2, max_length=32)
    title: str = Field(min_length=1, max_length=200)

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, v: str) -> str:
        v = v.strip().upper()
        # allow letters/digits/hyphen
        import re
        if not re.fullmatch(r"[A-Z0-9-]+", v):
            raise ValueError("code must be alphanumeric uppercase with optional hyphens")
        return v

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    code: Optional[str] = None
    title: Optional[str] = None

class CourseRead(CourseBase):
    id: int
    model_config = {"from_attributes": True}

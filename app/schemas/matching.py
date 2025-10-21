from __future__ import annotations
from pydantic import BaseModel, Field, conlist
from typing import List, Optional, Dict

class MatchInput(BaseModel):
    user_ids: conlist(int, min_length=2)  # at least 2 users to match
    group_size: int = Field(4, ge=2, le=10)
    min_overlap_minutes: int = Field(60, ge=15, le=600)
    course_id: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "user_ids": [1, 2, 3, 4, 5, 6],
                "group_size": 3,
                "min_overlap_minutes": 60,
                "course_id": 1
            }]
        }
    }

class MatchSlot(BaseModel):
    weekday: int  # 0..6
    start_min: int
    end_min: int

class MatchGroup(BaseModel):
    user_ids: List[int]
    slot: MatchSlot

class MatchPlan(BaseModel):
    groups: List[MatchGroup]
    leftovers: List[int]  # users we couldn't place
    params: Dict[str, int | None]
class MatchCourseInput(BaseModel):
    group_size: int = Field(4, ge=2, le=10)
    min_overlap_minutes: int = Field(60, ge=15, le=600)

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "group_size": 4,
                "min_overlap_minutes": 60
            }]
        }
    }

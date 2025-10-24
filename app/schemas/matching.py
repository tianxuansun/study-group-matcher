from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class MatchSlot(BaseModel):
    weekday: int
    start_min: int
    end_min: int

class MatchGroup(BaseModel):
    user_ids: List[int]
    slot: MatchSlot

class MatchInput(BaseModel):
    user_ids: List[int]
    group_size: int = Field(ge=2)
    min_overlap_minutes: int = Field(ge=1)
    course_id: Optional[int] = None
    # NEW (optional) knobs:
    allow_partial_last_group: bool = False
    name_prefix: Optional[str] = None  # if None, service uses "Auto Group"

class MatchCourseInput(BaseModel):
    group_size: int = Field(ge=2)
    min_overlap_minutes: int = Field(ge=1)
    # NEW (optional) knobs mirrored for by-course
    allow_partial_last_group: bool = False
    name_prefix: Optional[str] = None

class MatchPlan(BaseModel):
    groups: List[MatchGroup]
    leftovers: List[int]
    # Keep a params dict for transparency / debugging
    params: Dict[str, Any]

class MatchCourseInput(BaseModel):
    group_size: int = Field(ge=2)
    min_overlap_minutes: int = Field(ge=1)
    allow_partial_last_group: bool = False
    name_prefix: Optional[str] = None
    skip_already_grouped: bool = True
    

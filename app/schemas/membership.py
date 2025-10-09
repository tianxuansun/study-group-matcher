from pydantic import BaseModel, Field
from typing import Literal

class MembershipBase(BaseModel):
    group_id: int
    user_id: int
    role: Literal["member", "leader"] = Field(default="member")

class MembershipCreate(MembershipBase):
    pass

class MembershipRead(MembershipBase):
    id: int
    model_config = {"from_attributes": True}

from pydantic import BaseModel, Field

class MembershipRead(BaseModel):
    id: int
    user_id: int
    group_id: int

    model_config = {"from_attributes": True}

class MembershipCreate(BaseModel):
    user_id: int = Field(..., ge=1)
    group_id: int = Field(..., ge=1)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"user_id": 1, "group_id": 1}
            ]
        }
    }

class MembershipUpdate(BaseModel):
    # We usually don't update memberships; included for completeness
    user_id: int | None = Field(None, ge=1)
    group_id: int | None = Field(None, ge=1)

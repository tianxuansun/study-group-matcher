from pydantic import BaseModel, Field, model_validator
from typing import Optional

class AvailabilityBase(BaseModel):
    user_id: int
    weekday: int = Field(ge=0, le=6)
    start_min: int = Field(ge=0, le=1440)
    end_min: int = Field(ge=0, le=1440)

    @model_validator(mode="after")
    def check_times(self):
        if self.end_min <= self.start_min:
            raise ValueError("end_min must be greater than start_min")
        return self

class AvailabilityCreate(AvailabilityBase):
    pass

class AvailabilityUpdate(BaseModel):
    weekday: Optional[int] = None
    start_min: Optional[int] = None
    end_min: Optional[int] = None

class AvailabilityRead(AvailabilityBase):
    id: int
    model_config = {"from_attributes": True}

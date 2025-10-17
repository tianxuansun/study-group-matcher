from pydantic import BaseModel, Field, model_validator

# -------- Read --------
class AvailabilityRead(BaseModel):
    id: int
    user_id: int
    weekday: int
    start_min: int
    end_min: int

    model_config = {"from_attributes": True}

# -------- Create (all required) --------
class AvailabilityCreate(BaseModel):
    user_id: int
    weekday: int = Field(..., ge=0, le=6)
    start_min: int = Field(..., ge=0, le=1440)
    end_min: int = Field(..., ge=0, le=1440)

    @model_validator(mode="after")
    def _check_create_constraints(self):
        if not (0 <= self.weekday <= 6):
            raise ValueError("weekday must be in 0..6")
        if not (0 <= self.start_min <= 1440) or not (0 <= self.end_min <= 1440):
            raise ValueError("start_min/end_min must be in 0..1440")
        if self.start_min >= self.end_min:
            raise ValueError("end_min must be greater than start_min")
        return self

# -------- Update (all OPTIONAL; only validate given fields) --------
class AvailabilityUpdate(BaseModel):
    weekday: int | None = Field(None, ge=0, le=6)
    start_min: int | None = Field(None, ge=0, le=1440)
    end_min: int | None = Field(None, ge=0, le=1440)

    @model_validator(mode="after")
    def _check_update_constraints(self):
        # Range checks if provided
        if self.weekday is not None and not (0 <= self.weekday <= 6):
            raise ValueError("weekday must be in 0..6")
        if self.start_min is not None and not (0 <= self.start_min <= 1440):
            raise ValueError("start_min must be in 0..1440")
        if self.end_min is not None and not (0 <= self.end_min <= 1440):
            raise ValueError("end_min must be in 0..1440")

        # Order check if BOTH present in the patch
        if (self.start_min is not None) and (self.end_min is not None):
            if self.start_min >= self.end_min:
                raise ValueError("end_min must be greater than start_min")
        return self

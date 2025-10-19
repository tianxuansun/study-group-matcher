from pydantic import BaseModel, Field

class GroupRead(BaseModel):
    id: int
    name: str
    course_id: int | None = None

    model_config = {"from_attributes": True}

class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    course_id: int | None = None

    # OpenAPI examples
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "Study Group A", "course_id": None},
                {"name": "EC523-Group-1", "course_id": 1},
            ]
        }
    }

class GroupUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    course_id: int | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "Renamed Group"},
                {"course_id": 2},
            ]
        }
    }

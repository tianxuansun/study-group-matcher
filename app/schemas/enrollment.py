from pydantic import BaseModel

class EnrollmentBase(BaseModel):
    user_id: int
    course_id: int

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentRead(EnrollmentBase):
    pass

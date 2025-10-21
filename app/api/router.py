from fastapi import APIRouter
from .routes import users, courses, availabilities, group, membership, matching, enrollment  # <- singular modules

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
api_router.include_router(availabilities.router, prefix="/availabilities", tags=["Availabilities"])
api_router.include_router(group.router, prefix="/groups", tags=["Groups"])
api_router.include_router(membership.router, prefix="/memberships", tags=["Memberships"])
api_router.include_router(enrollment.router, prefix="/enrollments", tags=["Enrollments"])
api_router.include_router(matching.router, prefix="/matching", tags=["Matching"])
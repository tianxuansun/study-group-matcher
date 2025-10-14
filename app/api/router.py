from fastapi import APIRouter
from .routes import users, courses, availabilities

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
api_router.include_router(availabilities.router, prefix="/availabilities", tags=["Availabilities"])
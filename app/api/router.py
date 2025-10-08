from fastapi import APIRouter

api_router = APIRouter()

# Later you'll do:
# from .routes import users, courses
# api_router.include_router(users.router, prefix="/users", tags=["Users"])

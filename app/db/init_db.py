from app.db.base import Base
from app.db.session import engine

# Import models so they are registered with Base.metadata
from app.models.user import User  # noqa: F401
from app.models.course import Course  # noqa: F401
from app.models.availability import Availability  # noqa: F401
from app.models.group import Group  # noqa: F401
from app.models.membership import Membership  # noqa: F401
# Association table user_courses is imported via course module

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()

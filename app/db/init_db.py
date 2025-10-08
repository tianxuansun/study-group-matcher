from app.db.base import Base
from app.db.session import engine

def init_db():
    # later: import models here so metadata includes them
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()

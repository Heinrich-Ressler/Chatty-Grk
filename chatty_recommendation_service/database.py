from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://chatty_user:chatty_pass@postgres:5432/chatty_db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"connect_timeout": 10}) #Это даст PostgreSQL 10 секунд на старт
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from models import Base
Base.metadata.create_all(bind=engine)

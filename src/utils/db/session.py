from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.utils.settings import Settings

Engine = create_engine(Settings.DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    bind=Engine,
    autocommit=False,
    autoflush=False
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
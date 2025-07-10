from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
Base = declarative_base()

DATABASE_URL = "mysql+pymysql://root:%40Admin2004@localhost:3306/privtalk_db"

engine = create_engine(DATABASE_URL) #, echo=True
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# ✅ Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
#Import models after Base is defined

from app.models import token, user
from app.models.message import Message
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
Base = declarative_base()

DATABASE_URL = "mysql+pymysql://root:%40Admin2004@localhost:3306/privtalk_db"

engine = create_engine(DATABASE_URL, echo=True) 
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

#Import models after Base is defined

from app.models import token, user 
Base.metadata.create_all(bind=engine)
from sqlalchemy import Column, Integer, String, Boolean  # type: ignore
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)         
    email = Column(String(255), unique=True, index=True)            
    hashed_password = Column(String(255))                           
    chattoken=Column(String(255), unique=True)
    profile_photo = Column(String(255), nullable=True)
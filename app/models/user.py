from sqlalchemy import Column, Integer, String, Boolean  # type: ignore
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)         # ✅ Add length
    email = Column(String(255), unique=True, index=True)            # ✅ Add length
    hashed_password = Column(String(255))                           # ✅ Add length
    is_verified = Column(Boolean, default=False)
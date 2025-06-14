# ✅ File: app/models/token.py

from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime
from app.database import Base  # Make sure this Base is from the same place as in database.py

class VerificationToken(Base):
    __tablename__ = "verification_tokens"  # ✅ Needed to map class to table

    email = Column(String(255), primary_key=True, index=True)
    username=Column(String(255), nullable=False)
    password = Column(String(255)) 
    token = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
     
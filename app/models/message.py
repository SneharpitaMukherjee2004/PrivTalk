from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_token = Column(String(255), nullable=False)
    sender = Column(String(255), nullable=False)
    receiver = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), default="sent")  # Options: sent, delivered, seen
    timestamp = Column(DateTime, default=datetime.utcnow)

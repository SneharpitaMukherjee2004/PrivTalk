# app/models/chatroom.py
from sqlalchemy import Column, String
from app.database import Base

class ChatRoom(Base):
    __tablename__ = "chatrooms"

    room_id = Column(String(255), primary_key=True, index=True)
    host_token = Column(String(255), nullable=False)
    peer_token = Column(String(255), nullable=False)

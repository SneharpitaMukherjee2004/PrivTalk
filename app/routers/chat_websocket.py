from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.message import Message
from datetime import datetime

router = APIRouter()

connections = {}  # key: token, value: list of WebSocket connections

from fastapi import WebSocket, WebSocketDisconnect, Query

@router.websocket("/ws/chat/{token}")
async def chat_ws(websocket: WebSocket, token: str, username: str = Query(...)):
    await websocket.accept()

    if token not in connections:
        connections[token] = []
    connections[token].append({"ws": websocket, "username": username})

    try:
        while True:
            data = await websocket.receive_text()

            # Typing signal
            if data == "__typing__":
                for conn in connections[token]:
                    if conn["ws"] != websocket:
                        await conn["ws"].send_text("__typing__")
                continue

            # Seen signal
            if data == "__seen__":
                continue

            # Store message in DB
            if not data.startswith("__"):
                db: Session = SessionLocal()
                msg = Message(
                    token=token,
                    sender=username,
                    content=data,
                    timestamp=datetime.utcnow()
                )
                db.add(msg)
                db.commit()
                db.close()

            # Broadcast to other users
            for conn in connections[token]:
                if conn["ws"] != websocket:
                    await conn["ws"].send_text(data)

    except WebSocketDisconnect:
        connections[token] = [c for c in connections[token] if c["ws"] != websocket]

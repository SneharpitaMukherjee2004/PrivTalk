from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.message import Message
from datetime import datetime

router = APIRouter()

connections = {}  # key: token, value: list of WebSocket connections

@router.websocket("/ws/chat/{token}")
async def chat_ws(websocket: WebSocket, token: str):
    await websocket.accept()
    if token not in connections:
        connections[token] = []
    connections[token].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            # Typing event
            if data == "__typing__":
                for conn in connections[token]:
                    if conn != websocket:
                        await conn.send_text("__typing__")
                continue

            # Delivered event
            elif data.startswith("__delivered__:"):
                message_id = int(data.split(":")[1])
                db = SessionLocal()
                msg = db.query(Message).filter(Message.id == message_id).first()
                if msg:
                    msg.status = "delivered"
                    db.commit()
                db.close()
                continue

            # Seen event
            elif data == "__seen__":
                db = SessionLocal()
                db.query(Message).filter(Message.chat_token == token).update({"status": "seen"})
                db.commit()
                db.close()
                continue

            # Save the message as sent
            db = SessionLocal()
            new_msg = Message(
                chat_token=token,
                sender="sender_username",  # Replace with real auth
                receiver="receiver_username",  # Replace with real logic
                content=data,
                status="sent",
                timestamp=datetime.utcnow()
            )
            db.add(new_msg)
            db.commit()
            msg_id = new_msg.id
            db.close()

            # Send message to all clients
            for conn in connections[token]:
                await conn.send_text(data)

    except WebSocketDisconnect:
        connections[token].remove(websocket)

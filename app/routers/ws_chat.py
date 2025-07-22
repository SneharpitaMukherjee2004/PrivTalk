from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.routing import APIRouter
from app.models.chatroom import ChatRoom
from sqlalchemy.orm import Session
from app.database import get_db
from typing import Dict

router = APIRouter()
active_connections: Dict[str, WebSocket] = {}

@router.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, chat_token: str, db: Session = Depends(get_db)):
    # ✅ Accept the connection
    await websocket.accept()

    # ✅ Check room existence
    room = db.query(ChatRoom).filter(ChatRoom.room_id == room_id).first()
    if not room:
        await websocket.send_text("❌ Room not found!")
        await websocket.close()
        return

    # ✅ Check if user is part of the room
    if chat_token != room.host_token and chat_token != room.peer_token:
        await websocket.send_text("❌ You are not authorized for this room.")
        await websocket.close()
        return

    # ✅ Add to active connections
    active_connections[chat_token] = websocket

    try:
        while True:
            data = await websocket.receive_text()

            # Send to the other user
            recipient_token = room.peer_token if chat_token == room.host_token else room.host_token
            recipient_ws = active_connections.get(recipient_token)

            if recipient_ws:
                await recipient_ws.send_text(data)
            else:
                await websocket.send_text("🔕 Peer not connected yet.")
    except WebSocketDisconnect:
        del active_connections[chat_token]

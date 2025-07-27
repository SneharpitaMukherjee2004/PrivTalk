from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.routing import APIRouter
from app.models.chatroom import ChatRoom
from sqlalchemy.orm import Session
from app.database import get_db
from typing import Dict
import json

router = APIRouter()
active_connections: Dict[str, WebSocket] = {}

@router.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    chat_token: str,
    db: Session = Depends(get_db)
):
    await websocket.accept()

    # ✅ Validate room
    room = db.query(ChatRoom).filter(ChatRoom.room_id == room_id).first()
    if not room:
        await websocket.send_text(json.dumps({"type": "error", "msg": "Room not found"}))
        await websocket.close()
        return

    # ✅ Validate token
    if chat_token not in [room.host_token, room.peer_token]:
        await websocket.send_text(json.dumps({"type": "error", "msg": "Unauthorized"}))
        await websocket.close()
        return

    # ✅ Save connection
    active_connections[chat_token] = websocket
    recipient_token = room.peer_token if chat_token == room.host_token else room.host_token

    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)

            # ✅ Handle terminate separately
            if data["type"] == "terminate":
                recipient_ws = active_connections.get(recipient_token)
                if recipient_ws:
                    await recipient_ws.send_text(json.dumps({"type": "terminate"}))
                break  # exit loop for the sender, they will be redirected


            # Broadcast to recipient if online
            recipient_ws = active_connections.get(recipient_token)
            if recipient_ws:
                await recipient_ws.send_text(json.dumps(data))

            # Seen acknowledgments → only go back to sender
            if data["type"] == "seen":
                if chat_token in active_connections:
                    await websocket.send_text(json.dumps({"type": "seen"}))

    except WebSocketDisconnect:
        active_connections.pop(chat_token, None)

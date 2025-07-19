# app/routers/ws_chat.py

from fastapi import WebSocket, WebSocketDisconnect, Cookie, APIRouter
from typing import Annotated, Dict, List
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Dict, List
from urllib.parse import parse_qs

router = APIRouter()
room_connections: Dict[str, List[WebSocket]] = {}

@router.websocket("/ws/chat/{room_id}")
async def chat_websocket(websocket: WebSocket, room_id: str):
    await websocket.accept()

    # Extract query parameters manually
    query = parse_qs(websocket.url.query)
    chat_token = query.get("chat_token", [None])[0]

    # Validate
    if not chat_token:
        await websocket.close(code=1008)
        return

    # Logically allow any token (you can validate more deeply using DB if needed)
    if room_id not in room_connections:
        room_connections[room_id] = []
    room_connections[room_id].append(websocket)

    try:
        while True:
            msg = await websocket.receive_text()
            for conn in room_connections[room_id]:
                if conn != websocket:
                    await conn.send_text(msg)
    except WebSocketDisconnect:
        room_connections[room_id].remove(websocket)

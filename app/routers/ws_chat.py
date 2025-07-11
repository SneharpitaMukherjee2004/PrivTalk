# app/routers/ws_chat.py

from fastapi import WebSocket, WebSocketDisconnect, Cookie, APIRouter
from typing import Annotated, Dict, List

router = APIRouter()
room_connections: Dict[str, List[WebSocket]] = {}

@router.websocket("/ws/chat/{room_id}")
async def chat_websocket(
    websocket: WebSocket,
    room_id: str,
    chat_token: Annotated[str, Cookie()] = None,
    connect_chat: Annotated[str, Cookie()] = None
):
    if not chat_token or not connect_chat or room_id != connect_chat:
        await websocket.close()
        return

    await websocket.accept()

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
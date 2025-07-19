from fastapi import APIRouter, Request, Depends, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.qrgenerator import create_qr_code
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# In-memory connection pool
connections = {}  
# key: token, value: list of WebSocket connections
from fastapi import WebSocket, WebSocketDisconnect, Query

@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket, token: str = Query(...), username: str = Query(...)):
    await websocket.accept()

    if token not in connections:
        connections[token] = []

    connections[token].append({"ws": websocket, "username": username})

    try:
        while True:
            data = await websocket.receive_text()
            for conn in connections[token]:
                if conn["ws"] != websocket:
                    await conn["ws"].send_text(f"{username}: {data}")
    except WebSocketDisconnect:
        connections[token] = [c for c in connections[token] if c["ws"] != websocket]









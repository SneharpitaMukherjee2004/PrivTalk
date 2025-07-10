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

# Serve "Connect New" page
@router.get("/connectnew", response_class=HTMLResponse)
def connect_new_user_page(request: Request):
    return templates.TemplateResponse("connecting_new.html", {"request": request})


# Serve "Connect Old" page
@router.get("/connectold", response_class=HTMLResponse)
def connect_old_user_page(request: Request):
    return templates.TemplateResponse("connecting_old.html", {"request": request})


# Set the second user's token into connect_chat cookie
@router.get("/start-chat")
def start_chat(request: Request, token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.chattoken == token).first()
    if user:
        #return RedirectResponse(url=f"/chat?token={token}")

        response = RedirectResponse(url=f"/chat?token={token}", status_code=302)
        response.set_cookie(
            key="connect_chat",
            value=token,
            httponly=True,
            max_age=3600,
            path="/",
            secure=False,
            samesite="Lax",
            #crosssite=True
        )
        return response
    else:
        return templates.TemplateResponse("connecting_new_failed.html", {
            "request": request,
            "error": "Invalid or expired chat token."
        })


# Serve the chat UI with correct user and target from cookies
@router.get("/chat")
async def chat(request: Request, token: str, db: Session = Depends(get_db)):
    current_username = request.cookies.get("current_user")
    print("All cookies:", request.cookies)
    print("current_user:", current_username)

    if not current_username:
        return JSONResponse(status_code=401, content={"detail": "Login expired. Please log in again."})

    # ✅ Fetch current user from DB
    current_user = db.query(User).filter(User.username == username).first()
    if not current_user:
        return HTMLResponse("Invalid user", status_code=401)

    # ✅ Fetch the connected user (via token)
    other_user = db.query(User).filter(User.chattoken == connect_chat).first()
    if not other_user:
        return HTMLResponse("Invalid chat token", status_code=401)

    return templates.TemplateResponse("chatting.html", {
        "request": request,
        "current_user": current_user.username,
        "other_user": other_user.username,
        "token": connect_chat
    })




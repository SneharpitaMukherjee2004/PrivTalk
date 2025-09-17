# app/routers/room.py
from fastapi import APIRouter, Request, Depends, Query, Form, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Annotated
import hashlib

from app.models.user import User
from app.models.chatroom import ChatRoom
from app.database import get_db
from app.services import qrgenerator, supabase

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# 🔐 Generate deterministic room_id
def generate_room_id(token1: str, token2: str) -> str:
    tokens = sorted([token1.strip(), token2.strip()])
    return hashlib.sha256("".join(tokens).encode()).hexdigest()


# ✅ Create a Chat Room
@router.get("/create-room")
def create_room(
    chat_token: str = Query(...),
    peer_token: str = Query(...),
    db: Session = Depends(get_db)
):
    if not chat_token or not peer_token:
        return RedirectResponse(url="/profile?error=missing_tokens", status_code=302)

    room_id = generate_room_id(chat_token, peer_token)

    # Save if not already present
    if not db.query(ChatRoom).filter_by(room_id=room_id).first():
        new_room = ChatRoom(room_id=room_id, host_token=chat_token, peer_token=peer_token)
        db.add(new_room)
        db.commit()

    # Generate & Upload meeting QR → Supabase
    qr_url = qrgenerator.create_meeting_qr(room_id)

    return RedirectResponse(
        url=f"/chatroom?room_id={room_id}&chat_token={chat_token}&qr_url={qr_url}",
        status_code=302
    )


# ✅ Render Joinroom Page
@router.get("/joinroom", response_class=HTMLResponse)
async def join_room_page(request: Request, my_token: str = ""):
    return templates.TemplateResponse("joinroom.html", {
        "request": request,
        "my_token": my_token
    })


# ✅ Join Room (form POST)
@router.post("/joinroom")
def join_room(
    request: Request,
    my_token: str = Form(...),
    room_id: str = Form(...),
    db: Session = Depends(get_db)
):
    room = db.query(ChatRoom).filter(ChatRoom.room_id == room_id).first()

    if not room:
        return templates.TemplateResponse("joinroom.html", {
            "request": request,
            "error": "Room not found"
        })

    if my_token in [room.host_token, room.peer_token]:
        return RedirectResponse(
            url=f"/chatroom?room_id={room_id}&chat_token={my_token}",
            status_code=302
        )

    return templates.TemplateResponse("joinroom.html", {
        "request": request,
        "error": "You are unauthorized to enter in this meeting"
    })


# ✅ Auto-login with cookie + join
@router.get("/start-chat")
def start_chat(
    room_id: str,
    chat_token: Annotated[str, Cookie()] = None,
    db: Session = Depends(get_db)
):
    if not chat_token:
        return RedirectResponse(url="/login", status_code=302)

    room = db.query(ChatRoom).filter_by(room_id=room_id).first()
    if not room:
        return RedirectResponse(url="/joinroom?error=room_not_found", status_code=302)

    if chat_token not in [room.host_token, room.peer_token]:
        return RedirectResponse(url="/joinroom?error=unauthorized", status_code=302)

    return RedirectResponse(url=f"/chatroom?room_id={room_id}&chat_token={chat_token}")


# ✅ Chatroom page
@router.get("/chatroom")
def chatroom_page(
    request: Request,
    room_id: str,
    chat_token: str,
    qr_url: str = "",
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.chattoken == chat_token).first()
    if not user:
        return RedirectResponse("/login")

    return templates.TemplateResponse("chatroom.html", {
        "request": request,
        "room_id": room_id,
        "chat_token": chat_token,
        "email": user.email,
        "username": user.username,
        "token": user.chattoken,
        "qr_url": qr_url
    })


# ✅ Terminate Room → Delete meeting folder from Supabase
import shutil

# ✅ Terminate Room → Delete meeting folder from Supabase + Local
@router.post("/terminate-room")
def terminate_room(room_id: str = Form(...), db: Session = Depends(get_db)):
    room = db.query(ChatRoom).filter_by(room_id=room_id).first()
    if not room:
        print("No meeting room id matched")
        return {"status": "error", "message": "Room not found"}

    # 1. Delete meeting folder from Supabase
    print("➡️ Deleting meeting from Supabase")
    supabase.delete_meeting_folder(room_id)

    # 2. Delete local meeting folder if exists
    local_dir = f"chat-media/assets/meetings/{room_id}"
    try:
        if os.path.exists(local_dir):
            shutil.rmtree(local_dir)
            print(f"✅ Local meeting folder deleted: {local_dir}")
        else:
            print(f"⚠️ Local folder not found: {local_dir}")
    except Exception as e:
        print(f"❌ Failed to delete local folder {local_dir}: {e}")

    # 3. Delete from DB
    db.delete(room)
    db.commit()

    return {"status": "success", "message": "Room terminated and data deleted"}

from fastapi import APIRouter, Request, Depends, Query, Form, Cookie
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Annotated
import hashlib, os
import qrcode

from app.models.user import User
from app.models.chatroom import ChatRoom
from app.database import get_db
from app.config import QR_DIR

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# 🔐 Helper to generate consistent room_id using sorted tokens
def generate_room_id(token1: str, token2: str) -> str:
    tokens = sorted([token1.strip(), token2.strip()])
    return hashlib.sha256("".join(tokens).encode()).hexdigest()

# 🔲 Generate & Save QR Code
def generate_room_qr(room_id: str) -> str:
    qr_path = os.path.join(QR_DIR, f"{room_id}.png")
    if not os.path.exists(qr_path):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,  # 📌 Increase size
            border=4
        )
        qr.add_data(room_id)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(qr_path)
    return f"/assets/qrcodes/{room_id}.png"

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

    # 🗂️ Save room only if not already present
    if not db.query(ChatRoom).filter_by(room_id=room_id).first():
        new_room = ChatRoom(room_id=room_id, host_token=chat_token, peer_token=peer_token)
        db.add(new_room)
        db.commit()

    # 🔳 Generate downloadable QR code
    qr_url = generate_room_qr(room_id)

    # 🚀 Redirect to chatroom.html
    return RedirectResponse(
        url=f"/chatroom?room_id={room_id}&chat_token={chat_token}&qr_url={qr_url}",
        status_code=302
    )


# ✅ Render Joinroom Page
@router.get("/joinroom")
def joinroom_page(request: Request):
    return templates.TemplateResponse("joinroom.html", {"request": request})


# ✅ Verify and Join Room (POST from joinroom.html)
@router.post("/attempt-join")
def attempt_join(
    request: Request,
    room_id: str = Form(...),
    chat_token: str = Form(...),
    db: Session = Depends(get_db)
):
    room = db.query(ChatRoom).filter_by(room_id=room_id).first()
    if not room:
        return templates.TemplateResponse("joinroom.html", {
            "request": request,
            "error": "Room not found"
        })

    if chat_token in [room.host_token, room.peer_token]:
        return RedirectResponse(
            url=f"/chatroom?room_id={room_id}&chat_token={chat_token}",
            status_code=302
        )

    return templates.TemplateResponse("joinroom.html", {
        "request": request,
        "error": "Access Denied"
    })


# ✅ Optional: Auto-login with Cookie + Join Room
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


@router.get("/chatroom")
def chatroom_page(request: Request, room_id: str, chat_token: str, qr_url: str = "", db: Session = Depends(get_db)):
    return templates.TemplateResponse("chatroom.html", {
        "request": request,
        "room_id": room_id,
        "chat_token": chat_token,
        "qr_url": qr_url
    })

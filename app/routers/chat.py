from fastapi import APIRouter # type: ignore

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/test")
def chat_test():
    return {"message": "Chat route is working"}

@router.get("/connect-token")
def connect_user(token: str):
    user = db.query(User).filter(User.chat_token == token).first()
    if not user:
        return {"success": False, "message": "Invalid token."}
    
    # Logic to connect current user with the found user
    # Save connection in DB or shared table

    return {"success": True, "message": "Connection successful!"}

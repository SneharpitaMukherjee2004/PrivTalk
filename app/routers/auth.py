from fastapi import APIRouter, HTTPException # type: ignore
from pydantic import BaseModel, EmailStr # type: ignore
import secrets
from app.services.email_service import send_verification_email
from app.services.token_service import generate_token
router = APIRouter()

class EmailRequest(BaseModel):
    email: EmailStr

@router.post("/verify")
def verify_email(req: EmailRequest):
    try:
        token =generate_token(16)
        send_verification_email(req.email, token)
        return {"message": "Verification email sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
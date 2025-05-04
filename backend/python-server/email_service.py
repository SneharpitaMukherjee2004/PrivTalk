from fastapi import FastAPI # type: ignore
from pydantic import BaseModel, EmailStr # type: ignore
import smtplib
from email.mime.text import MIMEText
import secrets
import os


from fastapi.middleware.cors import CORSMiddleware # type: ignore

app = FastAPI()

# Allow requests from all origins (or specify your Spring Boot server origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with ["http://localhost:8080"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailRequest(BaseModel):
    email: EmailStr

@app.post("/send-verification")
def send_verification(req: EmailRequest):
    token = secrets.token_urlsafe(16)
    link = f"http://localhost:8080/verify-email?token={token}"

    sender = "privtalk8@gmail.com"
    password = "ygtdgvfwoifcqeap"  # Use App Password, NOT your Gmail password
    receiver = req.email

    msg = MIMEText(f"Click the link to verify your email:\n{link}")
    msg["Subject"] = "Verify your email"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
            print(f"email send! to {receiver}")
        return {"message": "Verification email sent successfully."}
    except Exception as e:
        return {"error": str(e)}

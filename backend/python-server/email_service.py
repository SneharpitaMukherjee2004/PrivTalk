from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
import secrets
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:8081"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailRequest(BaseModel):
    email: EmailStr


@app.post("/send-verification")
def send_verification(req: EmailRequest):
    token = secrets.token_urlsafe(16)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    link = f"http://localhost:8081/verify-email?token={token}"

    sender = "privtalk8@gmail.com"
    password = "ygtdgvfwoifcqeap"
    receiver = req.email

    html_body = f"""
    <html>
    <body>
        <p>Dear User,<br><br>
        Thank you for registering with PrivTalk.<br><br>
        Please verify your email using the link below:<br><br>
        <a href="{link}">Verify Your Email</a><br><br>
        
        Sent at: <b>{timestamp}</b><br><br>
        Regards,<br>
        The PrivTalk Team
        </p>
    </body>
    </html>
    """

    msg = MIMEText(html_body, "html")
    msg["Subject"] = f"Verify your email - {timestamp}"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
            print(f"Email sent to {receiver}")
        return {"message": "Verification email sent successfully."}
    except Exception as e:
        return {"error": str(e)}
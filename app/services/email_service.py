#email_service.py
from app.database import SessionLocal
from app.models.token import VerificationToken
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
def send_verification_email(email: str, token: str, password: str,username:str):
    db = SessionLocal()

    existing = db.query(VerificationToken).filter_by(email=email).first()
    if existing:
        db.delete(existing)
        db.commit()

    new_entry = VerificationToken(
        email=email,
        username=username,
        password=password,
        token=token,
        is_verified=False,
        
    )
    db.add(new_entry)
    db.commit()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    link = f"http://localhost:8000/verify-email?token={token}"

    sender = "privtalk8@gmail.com"
    password = "ygtdgvfwoifcqeap"  # Use an app password for Gmail

    html_body = f"""
    <html>
    <body>
        <p>Dear User,<br><br>
        Thank you for registering with <strong>PrivTalk</strong>.<br><br>
        Please verify your email by clicking the link below:<br><br>
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
    msg["To"] = email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, email, msg.as_string())
            print(f"[SUCCESS] Email sent to {email}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        traceback.print_exc()
        raise Exception(f"Error sending email: {e}")
#token_service.py
import secrets

def generate_token(length: int = 16) -> str:
    return secrets.token_urlsafe(length)



        
def chat_token():
    return generate_token(32)
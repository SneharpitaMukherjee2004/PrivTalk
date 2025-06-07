import secrets

def generate_token(length: int = 16) -> str:
    return secrets.token_urlsafe(length)

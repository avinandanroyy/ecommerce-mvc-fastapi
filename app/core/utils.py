import hashlib
import secrets


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def generate_hashed_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_uid() -> str:
    return secrets.token_hex(8)

from functools import wraps
from http import HTTPStatus

from fastapi import HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_token
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def require_auth(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        return payload
    except ValueError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_admin(auth_data: dict = Depends(require_auth)):
    role = auth_data.get("role", "")
    if role != "admin":
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You don't have permission to perform this action",
        )
    return auth_data


def require_role(required_role: str):
    def wrapper(auth_data: dict = Depends(require_auth)):
        role = auth_data.get("role", "")
        if role != required_role:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail=f"You don't have permission to perform this action. Required role: {required_role}",
            )
        return auth_data
    return wrapper


def rate_limit(max_requests: int = settings.RATE_LIMIT_REQUESTS, window_seconds: int = settings.RATE_LIMIT_WINDOW):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request") or (args[0] if args else None)
            if not isinstance(request, Request):
                return await func(*args, **kwargs)
            
            client_ip = request.client.host if request.client else "unknown"
            key = f"ratelimit:{client_ip}:{func.__name__}"
            
            # Redis rate limiting would go here
            return await func(*args, **kwargs)
        return wrapper
    return decorator

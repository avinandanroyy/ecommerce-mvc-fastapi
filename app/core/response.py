from typing import Any
from fastapi import Response
from pydantic import BaseModel


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: Any


class SuccessResponse(BaseModel):
    success: bool = True
    data: Any
    message: str = "Success"
    code: int = 200


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    code: int
    details: Any = None

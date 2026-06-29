from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import Any

from app.schemas.user import UserCreate, UserLogin, UserUpdate, Token, UserResponse
from app.schemas.product import ProductResponse
from app.services.user_service import UserService
from app.core.deps import get_db, require_auth
from app.core.response import SuccessResponse, ErrorResponse, AuthResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthResponse, responses={201: {"model": AuthResponse}})
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    try:
        user_service = UserService(db)
        user = user_service.register(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        if not user:
            return Response(
                content=ErrorResponse(
                    error="Registration failed",
                    message="Failed to create user",
                    code=400
                ).model_dump(),
                status_code=400,
                media_type="application/json"
            )
        
        from app.core.security import create_access_token, create_refresh_token
        access_token = create_access_token(data={"sub": user.id, "role": user.role})
        refresh_token = create_refresh_token(data={"sub": user.id, "role": user.role})
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=bool(user.is_active),
            created_at=user.created_at
        )
        
        return Response(
            content=AuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user=user_response.model_dump()
            ).model_dump(),
            status_code=201,
            media_type="application/json"
        )
    except ValueError as e:
        return Response(
            content=ErrorResponse(
                error="Registration failed",
                message=str(e),
                code=400
            ).model_dump(),
            status_code=400,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(),
            status_code=500,
            media_type="application/json"
        )

@router.post("/login", response_model=AuthResponse)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    try:
        user_service = UserService(db)
        user = user_service.login(
            email=user_data.email,
            password=user_data.password
        )
        if not user:
            return Response(
                content=ErrorResponse(
                    error="Authentication failed",
                    message="Invalid email or password",
                    code=401
                ).model_dump(),
                status_code=401,
                media_type="application/json"
            )
        
        from app.core.security import create_access_token, create_refresh_token
        access_token = create_access_token(data={"sub": user.id, "role": user.role})
        refresh_token = create_refresh_token(data={"sub": user.id, "role": user.role})
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=bool(user.is_active),
            created_at=user.created_at
        )
        
        return Response(
            content=AuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user=user_response.model_dump()
            ).model_dump(),
            status_code=200,
            media_type="application/json"
        )
    except ValueError as e:
        return Response(
            content=ErrorResponse(
                error="Authentication failed",
                message=str(e),
                code=401
            ).model_dump(),
            status_code=401,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(),
            status_code=500,
            media_type="application/json"
        )

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
) -> Any:
    try:
        from app.core.security import decode_token, create_access_token, create_refresh_token
        
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
        
        user_service = UserService(db)
        user = user_service.get_by_id(user_id)
        if not user:
            return Response(
                content=ErrorResponse(
                    error="Token refresh failed",
                    message="User not found",
                    code=401
                ).model_dump(),
                status_code=401,
                media_type="application/json"
            )
        
        access_token = create_access_token(data={"sub": user.id, "role": user.role})
        new_refresh_token = create_refresh_token(data={"sub": user.id, "role": user.role})
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=bool(user.is_active),
            created_at=user.created_at
        )
        
        return Response(
            content=AuthResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                user=user_response.model_dump()
            ).model_dump(),
            status_code=200,
            media_type="application/json"
        )
    except ValueError as e:
        return Response(
            content=ErrorResponse(
                error="Token refresh failed",
                message=str(e),
                code=401
            ).model_dump(),
            status_code=401,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(),
            status_code=500,
            media_type="application/json"
        )

@router.post("/logout", response_model=SuccessResponse)
async def logout(
    db: Session = Depends(get_db)
) -> Any:
    try:
        return Response(
            content=SuccessResponse(
                data={},
                message="Successfully logged out",
                code=200
            ).model_dump(),
            status_code=200,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=ErrorResponse(
                error="Logout failed",
                message=str(e),
                code=500
            ).model_dump(),
            status_code=500,
            media_type="application/json"
        )

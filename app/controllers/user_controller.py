from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import Any

from app.services.user_service import UserService
from app.core.deps import get_db, require_auth, require_admin
from app.core.response import SuccessResponse, ErrorResponse
from app.schemas.user import UserUpdate, UserResponse, UserCreate, UserLogin

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.get("/", response_model=SuccessResponse)
async def get_current_user(
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    try:
        user_service = UserService(db)
        user = user_service.get_by_id(auth_data.get("sub"))
        
        if not user:
            return Response(
                content=ErrorResponse(
                    error="User not found",
                    message="User does not exist",
                    code=404
                ).model_dump(),
                status_code=404,
                media_type="application/json"
            )
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=bool(user.is_active),
            created_at=user.created_at
        )
        
        return Response(
            content=SuccessResponse(
                data={"user": user_response.model_dump()},
                message="User retrieved successfully",
                code=200
            ).model_dump(),
            status_code=200,
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

@router.put("/", response_model=SuccessResponse)
async def update_current_user(
    user_data: UserUpdate,
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    try:
        user_service = UserService(db)
        user = user_service.get_by_id(auth_data.get("sub"))
        
        if not user:
            return Response(
                content=ErrorResponse(
                    error="User not found",
                    message="User does not exist",
                    code=404
                ).model_dump(),
                status_code=404,
                media_type="application/json"
            )
        
        update_data = user_data.model_dump(exclude_unset=True)
        updated_user = user_service.update_profile(user.id, **update_data)
        
        user_response = UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            name=updated_user.name,
            role=updated_user.role,
            is_active=bool(updated_user.is_active),
            created_at=updated_user.created_at
        )
        
        return Response(
            content=SuccessResponse(
                data={"user": user_response.model_dump()},
                message="User updated successfully",
                code=200
            ).model_dump(),
            status_code=200,
            media_type="application/json"
        )
    except ValueError as e:
        return Response(
            content=ErrorResponse(
                error="Update failed",
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

@router.get("/{user_id}", response_model=SuccessResponse)
async def get_user_by_id(
    user_id: int,
    auth_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Any:
    try:
        user_service = UserService(db)
        user = user_service.get_by_id(user_id)
        
        if not user:
            return Response(
                content=ErrorResponse(
                    error="User not found",
                    message="User does not exist",
                    code=404
                ).model_dump(),
                status_code=404,
                media_type="application/json"
            )
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=bool(user.is_active),
            created_at=user.created_at
        )
        
        return Response(
            content=SuccessResponse(
                data={"user": user_response.model_dump()},
                message="User retrieved successfully",
                code=200
            ).model_dump(),
            status_code=200,
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

@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: int,
    auth_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Any:
    try:
        user_service = UserService(db)
        user = user_service.get_by_id(user_id)
        
        if not user:
            return Response(
                content=ErrorResponse(
                    error="User not found",
                    message="User does not exist",
                    code=404
                ).model_dump(),
                status_code=404,
                media_type="application/json"
            )
        
        success = user_service.delete_user(user_id)
        
        if not success:
            return Response(
                content=ErrorResponse(
                    error="Delete failed",
                    message="Failed to delete user",
                    code=400
                ).model_dump(),
                status_code=400,
                media_type="application/json"
            )
        
        return Response(
            content=SuccessResponse(
                data={},
                message="User deleted successfully",
                code=200
            ).model_dump(),
            status_code=200,
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

@router.get("/", response_model=SuccessResponse)
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    auth_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Any:
    try:
        user_service = UserService(db)
        users = user_service.list_all(skip=skip, limit=limit)
        
        user_responses = []
        for user in users:
            user_response = UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                role=user.role,
                is_active=bool(user.is_active),
                created_at=user.created_at
            )
            user_responses.append(user_response.model_dump())
        
        return Response(
            content=SuccessResponse(
                data={"users": user_responses, "total": len(user_responses)},
                message="Users retrieved successfully",
                code=200
            ).model_dump(),
            status_code=200,
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

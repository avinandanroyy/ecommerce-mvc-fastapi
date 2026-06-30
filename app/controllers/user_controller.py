from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any

from app.services.user_service import UserService
from app.core.database import get_db
from app.core.deps import require_auth, require_admin
from app.core.response import SuccessResponse, ErrorResponse
from app.schemas.user import UserUpdate, UserResponse, UserCreate, UserLogin

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.get("/me", response_model=SuccessResponse)
async def get_current_user(
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    try:
        user_service = UserService(db)
        user = user_service.get_by_id(auth_data.get("sub"))
        
        if not user:
            return JSONResponse(
                content=ErrorResponse(
                    error="User not found",
                    message="User does not exist",
                    code=404
                ).model_dump(mode="json"),
                status_code=404
            )
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=bool(user.is_active),
            created_at=user.created_at
        )
        
        return JSONResponse(
            content=SuccessResponse(
                data={"user": user_response.model_dump(mode="json")},
                message="User retrieved successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(mode="json"),
            status_code=500
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
            return JSONResponse(
                content=ErrorResponse(
                    error="User not found",
                    message="User does not exist",
                    code=404
                ).model_dump(mode="json"),
                status_code=404
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
        
        return JSONResponse(
            content=SuccessResponse(
                data={"user": user_response.model_dump(mode="json")},
                message="User updated successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except ValueError as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Update failed",
                message=str(e),
                code=400
            ).model_dump(mode="json"),
            status_code=400
        )
    except Exception as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(mode="json"),
            status_code=500
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
            return JSONResponse(
                content=ErrorResponse(
                    error="User not found",
                    message="User does not exist",
                    code=404
                ).model_dump(mode="json"),
                status_code=404
            )
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=bool(user.is_active),
            created_at=user.created_at
        )
        
        return JSONResponse(
            content=SuccessResponse(
                data={"user": user_response.model_dump(mode="json")},
                message="User retrieved successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(mode="json"),
            status_code=500
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
            return JSONResponse(
                content=ErrorResponse(
                    error="User not found",
                    message="User does not exist",
                    code=404
                ).model_dump(mode="json"),
                status_code=404
            )
        
        success = user_service.delete_user(user_id)
        
        if not success:
            return JSONResponse(
                content=ErrorResponse(
                    error="Delete failed",
                    message="Failed to delete user",
                    code=400
                ).model_dump(mode="json"),
                status_code=400
            )
        
        return JSONResponse(
            content=SuccessResponse(
                data={},
                message="User deleted successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(mode="json"),
            status_code=500
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
            user_responses.append(user_response.model_dump(mode="json"))
        
        return JSONResponse(
            content=SuccessResponse(
                data={"users": user_responses, "total": len(user_responses)},
                message="Users retrieved successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(mode="json"),
            status_code=500
        )

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import Any

from app.services.category_service import CategoryService
from app.core.deps import get_db, require_admin
from app.core.response import SuccessResponse, ErrorResponse
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])

@router.post("/", response_model=SuccessResponse)
async def create_category(
    category_data: CategoryCreate,
    auth_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Any:
    try:
        category_service = CategoryService(db)
        category = category_service.create(
            name=category_data.name,
            description=category_data.description
        )
        
        category_response = CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
        
        return Response(
            content=SuccessResponse(
                data={"category": category_response.model_dump()},
                message="Category created successfully",
                code=201
            ).model_dump(),
            status_code=201,
            media_type="application/json"
        )
    except ValueError as e:
        return Response(
            content=ErrorResponse(
                error="Category creation failed",
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

@router.get("/", response_model=SuccessResponse)
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    try:
        category_service = CategoryService(db)
        categories = category_service.list_all_active(skip=skip, limit=limit)
        
        category_responses = []
        for category in categories:
            category_response = CategoryListResponse(
                id=category.id,
                name=category.name,
                description=category.description,
                is_active=category.is_active,
                created_at=category.created_at
            )
            category_responses.append(category_response.model_dump())
        
        return Response(
            content=SuccessResponse(
                data={"categories": category_responses, "total": len(category_responses)},
                message="Categories retrieved successfully",
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

@router.get("/{category_id}", response_model=SuccessResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
) -> Any:
    try:
        category_service = CategoryService(db)
        category = category_service.get_by_id(category_id)
        
        if not category:
            return Response(
                content=ErrorResponse(
                    error="Category not found",
                    message="Category does not exist",
                    code=404
                ).model_dump(),
                status_code=404,
                media_type="application/json"
            )
        
        category_response = CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
        
        return Response(
            content=SuccessResponse(
                data={"category": category_response.model_dump()},
                message="Category retrieved successfully",
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

@router.put("/{category_id}", response_model=SuccessResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    auth_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Any:
    try:
        category_service = CategoryService(db)
        category = category_service.update(
            category_id=category_id,
            name=category_data.name,
            description=category_data.description
        )
        
        if not category:
            return Response(
                content=ErrorResponse(
                    error="Category not found",
                    message="Category does not exist",
                    code=404
                ).model_dump(),
                status_code=404,
                media_type="application/json"
            )
        
        category_response = CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
        
        return Response(
            content=SuccessResponse(
                data={"category": category_response.model_dump()},
                message="Category updated successfully",
                code=200
            ).model_dump(),
            status_code=200,
            media_type="application/json"
        )
    except ValueError as e:
        return Response(
            content=ErrorResponse(
                error="Category update failed",
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

@router.delete("/{category_id}", response_model=SuccessResponse)
async def delete_category(
    category_id: int,
    auth_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Any:
    try:
        category_service = CategoryService(db)
        category = category_service.delete(category_id)
        
        if not category:
            return Response(
                content=ErrorResponse(
                    error="Category not found",
                    message="Category does not exist",
                    code=404
                ).model_dump(),
                status_code=404,
                media_type="application/json"
            )
        
        return Response(
            content=SuccessResponse(
                data={},
                message="Category deleted successfully",
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

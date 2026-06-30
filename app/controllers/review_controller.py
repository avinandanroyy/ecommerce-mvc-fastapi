from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any

from app.services.review_service import ReviewService
from app.core.database import get_db
from app.core.deps import require_auth
from app.core.response import SuccessResponse, ErrorResponse
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse

router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])

@router.post("/", response_model=SuccessResponse)
async def create_review(
    review_data: ReviewCreate,
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    try:
        review_service = ReviewService(db)
        review = review_service.create_review(
            user_id=auth_data.get("sub"),
            product_id=review_data.product_id,
            rating=review_data.rating,
            review_text=review_data.review_text
        )
        
        review_response = ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            product_id=review.product_id,
            rating=review.rating,
            review_text=review.review_text,
            created_at=review.created_at,
            updated_at=review.updated_at
        )
        
        return JSONResponse(
            content=SuccessResponse(
                data={"review": review_response.model_dump(mode="json")},
                message="Review created successfully",
                code=201
            ).model_dump(mode="json"),
            status_code=201
        )
    except ValueError as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Review creation failed",
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

@router.get("/product/{product_id}", response_model=SuccessResponse)
async def get_product_reviews(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    pagination = {"skip": skip, "limit": limit}
    try:
        review_service = ReviewService(db)
        reviews = review_service.get_reviews_by_product(
            product_id=product_id,
            skip=pagination.get("skip", 0),
            limit=pagination.get("limit", 100)
        )
        
        reviews_data = []
        for review in reviews:
            reviews_data.append({
                "id": review.id,
                "user_id": review.user_id,
                "rating": review.rating,
                "review_text": review.review_text,
                "created_at": review.created_at
            })
        
        page = pagination.get("skip", 0) // pagination.get("limit", 100) + 1 if pagination.get("limit", 100) else 1
        total_pages = (len(reviews) + pagination.get("limit", 100) - 1) // pagination.get("limit", 100) if pagination.get("limit", 100) and reviews else 0
        
        return JSONResponse(
            content=SuccessResponse(
                data={
                    "reviews": reviews_data,
                    "total": len(reviews),
                    "page": page,
                    "page_size": pagination.get("limit", 100),
                    "total_pages": total_pages
                },
                message="Reviews retrieved successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except ValueError as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Review retrieval failed",
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

@router.put("/{review_id}", response_model=SuccessResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    try:
        review_service = ReviewService(db)
        review = review_service.update_review(
            review_id=review_id,
            user_id=auth_data.get("sub"),
            rating=review_data.rating,
            review_text=review_data.review_text
        )
        
        if not review:
            return JSONResponse(
                content=ErrorResponse(
                    error="Review not found",
                    message="Review does not exist",
                    code=404
                ).model_dump(mode="json"),
                status_code=404
            )
        
        review_response = ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            product_id=review.product_id,
            rating=review.rating,
            review_text=review.review_text,
            created_at=review.created_at,
            updated_at=review.updated_at
        )
        
        return JSONResponse(
            content=SuccessResponse(
                data={"review": review_response.model_dump(mode="json")},
                message="Review updated successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except ValueError as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Review update failed",
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

@router.delete("/{review_id}", response_model=SuccessResponse)
async def delete_review(
    review_id: int,
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    try:
        review_service = ReviewService(db)
        success = review_service.delete_review(
            review_id=review_id,
            user_id=auth_data.get("sub")
        )
        
        if not success:
            return JSONResponse(
                content=ErrorResponse(
                    error="Review not found",
                    message="Review does not exist",
                    code=404
                ).model_dump(mode="json"),
                status_code=404
            )
        
        return JSONResponse(
            content=SuccessResponse(
                data={},
                message="Review deleted successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except ValueError as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Review deletion failed",
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

@router.get("/stats/{product_id}", response_model=SuccessResponse)
async def get_product_stats(
    product_id: int,
    db: Session = Depends(get_db)
) -> Any:
    try:
        review_service = ReviewService(db)
        stats = review_service.get_product_stats(product_id=product_id)
        
        return JSONResponse(
            content=SuccessResponse(
                data={"stats": stats},
                message="Product stats retrieved successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except ValueError as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Product stats retrieval failed",
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

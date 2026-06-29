from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import Any

from app.services.cart_service import CartService
from app.core.deps import get_db, require_auth
from app.core.response import SuccessResponse, ErrorResponse
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse

router = APIRouter(prefix="/api/v1/cart", tags=["Cart"])

@router.get("/", response_model=SuccessResponse)
async def get_cart(
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    try:
        cart_service = CartService(db)
        cart = cart_service.get_cart(auth_data.get("sub"))
        
        return Response(
            content=SuccessResponse(
                data={"cart": cart},
                message="Cart retrieved successfully",
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

@router.post("/items", response_model=SuccessResponse)
async def add_to_cart(
    cart_item_data: CartItemCreate,
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    try:
        cart_service = CartService(db)
        cart = cart_service.add_item(
            user_id=auth_data.get("sub"),
            product_id=cart_item_data.product_id,
            quantity=cart_item_data.quantity
        )
        
        return Response(
            content=SuccessResponse(
                data={"cart": cart},
                message="Item added to cart",
                code=201
            ).model_dump(),
            status_code=201,
            media_type="application/json"
        )
    except ValueError as e:
        return Response(
            content=ErrorResponse(
                error="Add to cart failed",
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

@router.put("/items/{product_id}", response_model=SuccessResponse)
async def update_cart_item(
    product_id: int,
    cart_item_data: CartItemUpdate,
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    try:
        cart_service = CartService(db)
        cart = cart_service.update_item(
            user_id=auth_data.get("sub"),
            product_id=product_id,
            quantity=cart_item_data.quantity
        )
        
        return Response(
            content=SuccessResponse(
                data={"cart": cart},
                message="Cart item updated successfully",
                code=200
            ).model_dump(),
            status_code=200,
            media_type="application/json"
        )
    except ValueError as e:
        return Response(
            content=ErrorResponse(
                error="Update cart item failed",
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

@router.delete("/items/{product_id}", response_model=SuccessResponse)
async def remove_from_cart(
    product_id: int,
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    try:
        cart_service = CartService(db)
        cart = cart_service.remove_item(
            user_id=auth_data.get("sub"),
            product_id=product_id
        )
        
        return Response(
            content=SuccessResponse(
                data={"cart": cart},
                message="Item removed from cart",
                code=200
            ).model_dump(),
            status_code=200,
            media_type="application/json"
        )
    except ValueError as e:
        return Response(
            content=ErrorResponse(
                error="Remove from cart failed",
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

@router.delete("/", response_model=SuccessResponse)
async def clear_cart(
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    try:
        cart_service = CartService(db)
        success = cart_service.clear_cart(auth_data.get("sub"))
        
        if not success:
            return Response(
                content=ErrorResponse(
                    error="Clear cart failed",
                    message="Failed to clear cart",
                    code=400
                ).model_dump(),
                status_code=400,
                media_type="application/json"
            )
        
        return Response(
            content=SuccessResponse(
                data={},
                message="Cart cleared successfully",
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

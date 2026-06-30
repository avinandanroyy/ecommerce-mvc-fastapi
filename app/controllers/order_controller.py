from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any

from app.services.order_service import OrderService
from app.core.database import get_db
from app.core.deps import require_auth, require_admin
from app.core.response import SuccessResponse, ErrorResponse
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderListResponse

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])

@router.post("/", response_model=SuccessResponse)
async def create_order(
    order_data: OrderCreate,
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    try:
        order_service = OrderService(db)
        order = order_service.create_order(
            user_id=auth_data.get("sub"),
            shipping_address=order_data.shipping_address,
            payment_method=order_data.payment_method
        )
        
        order_response = OrderResponse(
            id=order.id,
            user_id=order.user_id,
            total_amount=order.total_amount,
            status=order.status,
            payment_status=order.payment_status,
            shipping_address=order.shipping_address,
            payment_method=order.payment_method,
            items=[],
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        
        return JSONResponse(
            content=SuccessResponse(
                data={"order": order_response.model_dump(mode="json")},
                message="Order created successfully",
                code=201
            ).model_dump(mode="json"),
            status_code=201
        )
    except ValueError as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Order creation failed",
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

@router.get("/", response_model=SuccessResponse)
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    pagination = {"skip": skip, "limit": limit}
    try:
        order_service = OrderService(db)
        orders = order_service.get_orders_by_user(
            user_id=auth_data.get("sub"),
            skip=pagination.get("skip", 0),
            limit=pagination.get("limit", 100)
        )
        
        orders_response = []
        for order in orders:
            order_response = OrderListResponse(
                id=order.id,
                total_amount=order.total_amount,
                status=order.status,
                payment_status=order.payment_status,
                created_at=order.created_at
            )
            orders_response.append(order_response.model_dump(mode="json"))
        
        return JSONResponse(
            content=SuccessResponse(
                data={"orders": orders_response, "total": len(orders_response)},
                message="Orders retrieved successfully",
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

@router.get("/{order_id}", response_model=SuccessResponse)
async def get_order(
    order_id: int,
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    try:
        order_service = OrderService(db)
        order = order_service.get_order(order_id)
        
        if not order:
            return JSONResponse(
                content=ErrorResponse(
                    error="Order not found",
                    message="Order does not exist",
                    code=404
                ).model_dump(mode="json"),
                status_code=404
            )
        
        if order.user_id != auth_data.get("sub") and auth_data.get("role") != "admin":
            return JSONResponse(
                content=ErrorResponse(
                    error="Access denied",
                    message="You can only view your own orders",
                    code=403
                ).model_dump(mode="json"),
                status_code=403
            )
        
        order_response = OrderResponse(
            id=order.id,
            user_id=order.user_id,
            total_amount=order.total_amount,
            status=order.status,
            payment_status=order.payment_status,
            shipping_address=order.shipping_address,
            payment_method=order.payment_method,
            items=[],
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        
        return JSONResponse(
            content=SuccessResponse(
                data={"order": order_response.model_dump(mode="json")},
                message="Order retrieved successfully",
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

@router.put("/{order_id}/status", response_model=SuccessResponse)
async def update_order_status(
    order_id: int,
    order_data: OrderUpdate,
    auth_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Any:
    try:
        order_service = OrderService(db)
        order = order_service.update_order_status(order_id=order_id, status=order_data.status)
        
        if not order:
            return JSONResponse(
                content=ErrorResponse(
                    error="Order not found",
                    message="Order does not exist",
                    code=404
                ).model_dump(mode="json"),
                status_code=404
            )
        
        order_response = OrderResponse(
            id=order.id,
            user_id=order.user_id,
            total_amount=order.total_amount,
            status=order.status,
            payment_status=order.payment_status,
            shipping_address=order.shipping_address,
            payment_method=order.payment_method,
            items=[],
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        
        return JSONResponse(
            content=SuccessResponse(
                data={"order": order_response.model_dump(mode="json")},
                message="Order status updated successfully",
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

@router.delete("/{order_id}", response_model=SuccessResponse)
async def cancel_order(
    order_id: int,
    auth_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
) -> Any:
    try:
        order_service = OrderService(db)
        success = order_service.cancel_order(order_id=order_id, user_id=auth_data.get("sub"))
        
        if not success:
            return JSONResponse(
                content=ErrorResponse(
                    error="Order not found",
                    message="Order does not exist",
                    code=404
                ).model_dump(mode="json"),
                status_code=404
            )
        
        return JSONResponse(
            content=SuccessResponse(
                data={},
                message="Order cancelled successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except ValueError as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Order cancellation failed",
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

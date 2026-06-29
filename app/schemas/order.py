from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class PaymentStatus(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    REFUNDED = "refunded"


class OrderBase(BaseModel):
    shipping_address: Optional[str] = None
    payment_method: Optional[str] = None
    payment_status: PaymentStatus = PaymentStatus.UNPAID


class OrderCreate(OrderBase):
    pass


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: float
    quantity: int

    class Config:
        from_attributes = True


class OrderResponse(OrderBase):
    id: int
    user_id: int
    total_amount: float
    status: OrderStatus
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = None
    payment_method: Optional[str] = None
    payment_status: Optional[PaymentStatus] = None


class OrderListResponse(BaseModel):
    id: int
    total_amount: float
    status: OrderStatus
    payment_status: str
    created_at: datetime

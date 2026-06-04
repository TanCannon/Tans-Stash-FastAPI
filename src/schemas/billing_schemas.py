from pydantic import BaseModel
from decimal import Decimal

class CreateOrderRequest(BaseModel):
    plan_id: str

class CreateOrderResponse(BaseModel):
    payment_id: int
    order_id: str
    amount: Decimal

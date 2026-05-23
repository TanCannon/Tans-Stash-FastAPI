from fastapi import APIRouter
from src.gateways.payment.mock_gateway import MockPaymentGateway


router = APIRouter(
    prefix="/api",
    tags=["billing"]
    )

payment_gateway = MockPaymentGateway()

@router.post("/create-order")
async def create_order_route(amount: int):
    #create the order
    order = payment_gateway.create_order(amount)

    return order

@router.post("/verify-payment")
async def verify_payment_route(data: dict):
    #verify signature
    is_signature_verified = payment_gateway.verify_payment(data["signature"])

    #then create a subscription
    #pretending subscription got created
    if (is_signature_verified):
        return {
            "message": "Success",
            "detail": "Plan purchased successfully."
        }

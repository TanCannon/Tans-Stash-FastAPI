from .base import BasePaymentGateway
import uuid

class MockPaymentGateway(BasePaymentGateway):
    '''
    This class is just an example of how to payment gateway class should look like, methods need to be implemented in real for a payment provider.
    '''
    def create_order(self, amount: int):
        #create razorpay order, razorpay return order_id
        #return the order_id to frontend
        return { 
            "order_id": f"mock_order_{uuid.uuid4()}",
            "amount": amount,
            "currency": 'INR'
            }

    def verify_payment(self, signature: str):
        return signature == "mock_signature"

class BasePaymentGateway:
    def create_order(self, amount: int):
        raise NotImplementedErrror

    def verify_payment(self, signature: str):
        raise NotImplementedErrror


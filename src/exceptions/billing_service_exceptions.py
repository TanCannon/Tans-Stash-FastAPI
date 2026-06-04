from .base_exception import AppException

class PaymentNotFoundError(AppException):
    status_code = 404

    def __init__(self):
        super().__init__("Payment record not found")


class InvalidPaymentSignatureError(AppException):
    status_code = 400

    def __init__(self):
        super().__init__("Invalid payment signature")
        
class PlanNotFoundError(AppException):
    status_code = 404
    def __init__(self):
        super().__init__("Plan not found")

class ActiveSubscriptionExistsError(AppException):
    status_code = 409
    def __init__(self):
        super().__init__("Active subscription already exists")

class DuplicatePaymentError(AppException):
    status_code = 409
    def __init__(self):
        super().__init__("This payment id already exists")

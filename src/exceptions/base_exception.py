class AppException(Exception):
    status_code = 500

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

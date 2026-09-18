from .base_exception import AppException


class UserRegistrationError(AppException):
    status_code = 500

    def __init__(self):
        super().__init__("Failed to register user.")


class UserAlreadyExistsError(AppException):
    status_code = 409

    def __init__(self):
        super().__init__("User already exists.")


class UserNotFoundError(AppException):
    status_code = 404

    def __init__(self):
        super().__init__("User not found.")



class InvalidCredentialsError(AppException):
    status_code = 401

    def __init__(self):
        super().__init__("Invalid email or password.")


class InvalidRefreshTokenError(AppException):
    status_code = 401

    def __init__(self):
        super().__init__("Invalid refresh token.")


class InvalidTokenTypeError(AppException):
    status_code = 401

    def __init__(self):
        super().__init__("Invalid token type.")

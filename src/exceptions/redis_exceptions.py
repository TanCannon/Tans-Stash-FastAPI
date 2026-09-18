class RedisUnavailableException(Exception):
    """
    Raised when redis is unavailable.
    """
    def _init_(self, message: str = "Redis service is unavailable"):
        self.message = message;
        super().__init__(self.message);

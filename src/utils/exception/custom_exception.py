# src/utils/exceptions/custom_exception.py

class CustomException(Exception):
    def __init__(
        self,
        status_code: int,
        message: str,
        data=None,
        success: bool = False,
    ):
        self.status_code = status_code
        self.message = message
        self.data = data
        self.success = success
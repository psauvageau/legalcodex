from typing import Optional


class LCException(Exception):
    """Base exception for LegalCodex."""
    pass


class LCValueError(LCException):
    """
    Exception raised for errors in the input value.
    """
    pass

    @classmethod
    def validate_type(cls,  value:object,
                            expected_type:type,
                            message:Optional[str]=None) -> None:
        if message is None:
            message = f"Expected value of type {expected_type.__name__}, got {type(value).__name__}"
        if not isinstance(value, expected_type):
            raise cls(message)



class QuotaExceeded(LCException):
    """Exception raised when API quota is exceeded."""
    def __init__(self) -> None:
        super().__init__(f"API quota exceeded")



class UserNotFound(LCException):
    """Exception raised when a user is not found."""
    def __init__(self, username: str) -> None:
        super().__init__(f"User '{username}' not found")


class LCException(Exception):
    """Base exception for LegalCodex."""
    pass



class QuotaExceeded(LCException):
    """Exception raised when API quota is exceeded."""
    def __init__(self, api_name:str) -> None:
        super().__init__(f"API quota exceeded for {api_name}")
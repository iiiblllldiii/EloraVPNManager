from src.exc import EloraApplicationError


class InvalidJSONFormatError(EloraApplicationError, Exception):
    """Exception raised for invalid JSON format."""

    def __init__(self, message: str = "Invalid JSON format"):
        self._message = message
        super().__init__(self._message)

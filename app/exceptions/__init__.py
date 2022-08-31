"""Custom exceptions for the web-app."""

class QuotaExceededError(Exception):
    """Raised when request quota for the day is utilized."""
    pass


class EntityNotFoundError(Exception):
    """Raised when authorized google account doesn't have a particular entity (channel, video, comments, etc) associated with it."""
    
    def __init__(self, entity: str, message: str) -> None:
        """Constructor for the Error.

        Args:
            entity (str): Describes which entity (channel/video/comment) is missing.
            message (str): Error message.
        """
        
        self.entity = entity
        self.message = message
        super().__init__(self.message)
        

class AccessTokenExpiredError(Exception):
    """Raised when authorization access token is expired."""
    pass
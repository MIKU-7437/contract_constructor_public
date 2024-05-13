class Error:
    """Base error structure of response"""
    def __init__(self, error_type: str, message: str, location: str | None = None, *args, **kwargs):
        self.error_type: str = error_type
        self.location: str | None = location
        self.message: str = message

    @property
    def dict(self) -> dict:
        return {
            'error_type': self.error_type,
            'location': self.location,
            'message': self.message
        }

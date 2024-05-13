from typing import Any
from pydantic import BaseModel


class OutputDataDTO(BaseModel):
    """
    Data validation to response
    """
    success: bool = True
    data: Any = None
    details: Any = None

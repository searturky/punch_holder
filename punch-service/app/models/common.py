from typing import Any
from pydantic import BaseModel


class ResponseOut(BaseModel):

    data: Any
    message: str = None
    code: int = 200
    success: bool = True
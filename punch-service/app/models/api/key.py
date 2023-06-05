from enum import Enum
from pydantic import BaseModel, Field


class KeyIn(BaseModel):

    code: str
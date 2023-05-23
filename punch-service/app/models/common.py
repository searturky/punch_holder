from typing import Any
from pydantic import BaseModel
from enum import Enum

class DBCollectionNames(str, Enum):

    USER_TOKEN = "user_token"
    REGISTER = "register"
from enum import Enum
from bson import ObjectId
from pydantic import BaseModel, Field
from app.models.extra import JsonObjectID


# class Token(BaseModel):

#     id: JsonObjectID = Field(default_factory=JsonObjectID, alias="_id")
#     token: str
#     token_type: TokenTypes
#     bound: bool = False

#     class Config:
#         json_encoders = {ObjectId: str}

#     @property
#     def is_admin_token(self) -> bool:
#         return self.token_type == TokenTypes.ADMIN or self.token_type == TokenTypes.SUPERUSER
    
#     @property
#     def is_superuser_token(self) -> bool:
#         return self.token_type == TokenTypes.SUPERUSER
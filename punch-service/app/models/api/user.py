from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.extra import JsonObjectID


class User(BaseModel):

    id: JsonObjectID = Field(default_factory=JsonObjectID, alias="_id")
    token: str

    class Config:
        json_encoders = {ObjectId: str}
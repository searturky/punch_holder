from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.extra import JsonObjectID


class RegisterIn(BaseModel):

    token: str
    user_account: str
    session_id: str
    login_token: str

class Register(BaseModel):

    id: JsonObjectID = Field(default_factory=JsonObjectID, alias="_id")
    token: str
    user_account: str
    session_id: str
    login_token: str

    class Config:
        json_encoders = {ObjectId: str}



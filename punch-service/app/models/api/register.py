from pydantic import BaseModel, Field


class RegisterIn(BaseModel):

    token: str
    user_account: str
    session_id: str
    login_token: str



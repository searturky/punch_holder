from pydantic import BaseModel, Field


class RegisterPunchTaskIn(BaseModel):

    user_account: str | None
    session_id: str | None
    login_token: str | None


class RegisterTestTaskIn(BaseModel):

    test_msg: str




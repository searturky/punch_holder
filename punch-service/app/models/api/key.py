from pydantic import BaseModel, Field
from app.schemas.api.key import KeyTypes


class KeyIn(BaseModel):

    type: KeyTypes
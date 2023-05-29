from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.api.key import Key


async def init_db(code: str):
    key: Key = Key.find_by(code=code)
    pass

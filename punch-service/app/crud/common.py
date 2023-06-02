import asyncio
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine
from app.database import engine, Base
from app.schemas.api.key import Key, KeyTypes


async def ensure_superuser_key(code: str):
    key = await Key.find_one_by(code=code)
    if not key:
        key = Key(code=code, key_type=KeyTypes.SUPERUSER)
        await key.save()
    ...


async def sync_table(engine: AsyncEngine, code: str):
    async with engine.begin() as conn:
        conn: AsyncConnection
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await ensure_superuser_key(code)


def init_db(code: str):
    loop = asyncio.get_running_loop()
    loop.create_task(sync_table(engine, code))

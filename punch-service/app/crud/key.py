from app.models.api.key import Key, KeyTypes
from app.models.common import DBCollectionNames
from app.schemas.api.key import KeyTypes, Key


async def get_key(key_code: str) -> Key:
    key = Key.find_one_by(code=key_code)
    doc = await db[DBCollectionNames.KEY].find_one({"key": key})
    return Key(**doc) if doc else None

async def bound_key(key: str) -> bool:
    doc = await db[DBCollectionNames.KEY].find_one_and_update({"key": key}, {"$set": {"bound": True}})
    return doc["bound"] if doc else False

async def unbound_key(key: str) -> bool:
    doc = await db[DBCollectionNames.KEY].find_one_and_update({"key": key}, {"$set": {"bound": False}})
    return doc["bound"] if doc else False
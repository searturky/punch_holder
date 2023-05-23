from app.models.api.user import User
from motor.core import AgnosticDatabase
from app.models.common import DBCollectionNames

async def get_user(db: AgnosticDatabase, token: str) -> User:
    doc = await db[DBCollectionNames.USER_TOKEN].find_one({"token": token})
    return User(**doc) if doc else None
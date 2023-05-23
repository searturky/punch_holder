from app.models.api.register import RegisterIn
from motor.core import AgnosticDatabase
from app.models.common import DBCollectionNames

async def is_register(db: AgnosticDatabase, token: str, user_account: str) -> bool:
    doc = await db[DBCollectionNames.REGISTER].find_one(
        {
            '$or': [
                { 'token': token },
                { 'user_account': user_account }
            ]
        }
    )
    return True if doc else False
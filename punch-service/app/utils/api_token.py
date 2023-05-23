import secrets
from motor.core import AgnosticDatabase


def gen_api_token() -> str:
    return secrets.token_urlsafe(32)


async def write_api_token_to_db(db: AgnosticDatabase) -> None:
    token = gen_api_token()
    await db["user_token"].insert_one({"token": token})


if __name__ == '__main__':
    import os
    import sys
    python_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    sys.path.append(python_path)
    from app.database import db, io_loop
    io_loop.run_until_complete(write_api_token_to_db(db))
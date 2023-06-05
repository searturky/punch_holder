from app.schemas.api.key import Key


async def get_key(key_code: str) -> Key:
    key = await Key.find_one_by(code=key_code)
    return key
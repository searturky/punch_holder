from app.schemas.api.key import Key, KeyTypes


async def get_key(key_code: str) -> Key:
    key = await Key.find_one_by(code=key_code)
    return key


async def create_new_key_by_type(key_type: KeyTypes) -> Key:
    key = Key(key_type=key_type, code=Key.gen_code())
    await key.save()
    return key
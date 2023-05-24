import asyncio
import motor.motor_asyncio
from asyncio import AbstractEventLoop
from motor.core import AgnosticDatabase
from typing import Any, Dict, cast
from fastapi.encoders import jsonable_encoder
from app.core.config import settings
from app.models.common import DBCollectionNames
from app.models.api.key import Key, KeyTypes


def create_db(io_loop: AbstractEventLoop=None):
    if io_loop is None:
        try:
            io_loop = asyncio.get_running_loop()
        except:
            try:
                io_loop = asyncio.get_event_loop()
            except:
                io_loop = asyncio.new_event_loop()

    return motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL, io_loop=io_loop).punch


def init_db(db: "AgnosticDatabase"):

    superuser_key = settings.SUPERUSER_KEY
    io_loop = asyncio.get_running_loop()

    async def do_init_db():
        doc = await db[DBCollectionNames.KEY].find_one({"key": superuser_key})
        if doc is None:
            super_user_key = Key(key=superuser_key, key_type=KeyTypes.SUPERUSER)
            await db[DBCollectionNames.KEY].insert_one(jsonable_encoder(super_user_key))

    io_loop.create_task(do_init_db())

io_loop = asyncio.get_event_loop()
async_mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL, io_loop=io_loop)
db = async_mongo_client.punch



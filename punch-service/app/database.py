import asyncio
import motor.motor_asyncio
from typing import Any, Dict, cast
from app.core.config import settings


def create_db(io_loop=None):
    if io_loop is None:
        try:
            io_loop = asyncio.get_running_loop()
        except:
            try:
                io_loop = asyncio.get_event_loop()
            except:
                io_loop = asyncio.new_event_loop()

    return motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL, io_loop=io_loop).punch


io_loop = asyncio.get_event_loop()
async_mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL, io_loop=io_loop)
db = async_mongo_client.punch


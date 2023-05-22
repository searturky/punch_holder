from pytz import utc
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from pymongo import MongoClient

client = MongoClient(settings.APSCHEDULER_MONGODB_URL)

job_stores = {
    'default': MongoDBJobStore(
        client=client,
    )
}

executors = {
    'default': AsyncIOExecutor(),
}

job_defaults = {
    'coalesce': True,
}

scheduler = AsyncIOScheduler(
    executors=executors,
    job_defaults=job_defaults,
    jobstores=job_stores
)
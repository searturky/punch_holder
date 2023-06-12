import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor


job_stores = {
    'default': SQLAlchemyJobStore(
        url=settings.SCHEDULER_PGSQL_URL
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
    jobstores=job_stores,
    timezone=pytz.timezone(settings.TIMEZONE)
)

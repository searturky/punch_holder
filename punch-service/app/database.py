from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeBase


Base:DeclarativeBase  = declarative_base()
engine = create_async_engine(
    settings.PGSQL_URL,
)
async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
...



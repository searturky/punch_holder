from typing import Any, Dict, cast
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.sql.selectable import Select
from sqlalchemy.engine.result import ScalarResult
from app.database import Base, async_session_factory, engine


class CommonBase(Base):

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    create_at: Mapped[DateTime] = Column(DateTime, server_default=func.now())
    update_at: Mapped[DateTime] = Column(DateTime, server_default=func.now(), onupdate=func.now())

    _async_session_factory = async_session_factory

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, data: Dict[str, Any]):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    @classmethod
    async def find_by_id(cls, query_id: int):
        async with cls._async_session_factory() as session:
            session: AsyncSession
            res: cls = await session.get(cls, query_id)
            return res

    @classmethod
    async def find_all(cls):
        async with cls._async_session_factory() as session:
            session: AsyncSession
            stmt = select(cls)
            return cast(ScalarResult, (await session.scalars(stmt))).all()

    @classmethod
    async def find_all_count(cls):
        async with cls._async_session_factory() as session:
            session: AsyncSession
            stmt = select(func.count(cls.id))
            return cast(ScalarResult, (await session.scalars(stmt))).first()
        
    @classmethod
    async def find_one_by(cls, **kwargs):
        async with cls._async_session_factory() as session:
            session: AsyncSession
            stmt = cast(Select, select(cls)).filter_by(**kwargs)
            return cast(ScalarResult, (await session.scalars(stmt))).first()

    @classmethod
    async def find_all_by(cls, **kwargs):
        async with cls._async_session_factory() as session:
            session: AsyncSession
            stmt = cast(Select, select(cls)).filter_by(**kwargs)
            return cast(ScalarResult, (await session.scalars(stmt))).all()

    async def save(self):
        async with self._async_session_factory() as session:
            session: AsyncSession
            async with session.begin():
                session.add(self)
                await session.commit()

    async def delete(self):
        async with self._async_session_factory() as session:
            session: AsyncSession
            async with session.begin():
                await session.delete(self)
                await session.commit()
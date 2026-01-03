
import logging
from datetime import datetime
from typing import TypeVar, Type, Any

from sqlalchemy import update, select, delete, DateTime, text, Update, Select, Delete, TextClause, Result
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from db.session import AsyncSessionLocal

T = TypeVar("T", bound="Model")
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class Manager:

    @classmethod
    async def create(cls: Type[T], **kwargs):
        async with AsyncSessionLocal() as session:
            try:
                value = cls(**kwargs)
                session.add(value)
                await session.commit()
                await session.refresh(value)
                return value
            except (IntegrityError, DataError, SQLAlchemyError) as e:
                await session.rollback()
                cls._handle_db_error(e)

    @classmethod
    async def all_(cls: Type[T], order_fields: list[str] = None):
        async with AsyncSessionLocal() as session:
            try:
                query: Select[Any] = select(cls)
                if order_fields:
                    query = query.order_by(*order_fields)
                results: Result[Any] = await session.execute(query)
                return results.scalars().all()
            except (SQLAlchemyError) as e:
                await session.rollback()
                cls._handle_db_error(e)

    @classmethod
    async def get(cls: Type[T], **filter_):
        async with AsyncSessionLocal() as session:
            try:
                query: Select[Any] = select(cls).filter_by(**filter_)
                result: Result[Any] = await session.execute(query)
                return result.scalars().first()
            except(SQLAlchemyError) as e:
                await session.rollback()
                cls._handle_db_error(e)

    @classmethod
    async def filter_(cls: Type[T], *filter_, order_by_fields: list[str] = None):
        async with AsyncSessionLocal() as session:
            try:
                query: Select[Any] = select(cls).where(*filter_)
                if order_by_fields:
                    query = query.order_by(*order_by_fields)
                result: Result[Any] = await session.execute(query)
                return result.scalars().all()
            except(SQLAlchemyError) as e:
                await session.rollback()
                cls._handle_db_error(e)

    @classmethod
    async def update(cls: Type[T], id_: int, **kwargs):
        async with AsyncSessionLocal() as session:
            try:
                query: Update = update(cls).filter_by(id=id_).values(**kwargs).returning(cls)
                result: Result[Any] = await session.execute(query)
                await session.commit()
                return result.scalar_one_or_none()
            except(SQLAlchemyError) as e:
                await session.rollback()
                cls._handle_db_error(e)

    @classmethod
    async def delete(cls: Type[T], id_: int):
        async with AsyncSessionLocal() as session:
            try:
                query: Delete = delete(cls).filter_by(id=id_)
                await session.execute(query)
                await session.commit()
                return True
            except(SQLAlchemyError) as e:
                await session.rollback()
                cls._handle_db_error(e)

    @classmethod
    async def query(cls: Type[T], query, all_: bool = False):
        async with AsyncSessionLocal() as session:
            try:
                result: Result[Any] = await session.execute(query)
                if all_:
                    return result.scalars().all()
                return result.scalars().first()
            except(SQLAlchemyError) as e:
                await session.rollback()
                cls._handle_db_error(e)

    @staticmethod
    async def core_get(query: str, **params):
        async with AsyncSessionLocal() as session:
            try:
                stmt: TextClause = text(query)
                result: Result[Any] = await session.execute(stmt, params)
                return result.mappings().all()
            except(SQLAlchemyError) as e:
                await session.rollback()
                Manager._handle_db_error(e)

    @staticmethod
    async def core_commit(query: str, **params):
        async with AsyncSessionLocal() as session:
            try:
                stmt: TextClause = text(query)
                await session.execute(stmt, params)
                await session.commit()
            except (SQLAlchemyError) as e:
                await session.rollback()
                Manager._handle_db_error(e)

    @staticmethod
    def _handle_db_error(e: Exception):
        if isinstance(e, IntegrityError):
            raise logger.error(msg=f"Ma'lumot nusxalangan: {str(e.orig)}")
        if isinstance(e, DataError):
            raise logger.error(msg=f"Noto'g'ri ma'lumot: {str(e.orig)}")
        raise logger.error(msg=f"Baza xatosi: {str(e)}")


tz: str = "CURRENT_TIMESTAMP"


class Model(Base, Manager):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text(tz))

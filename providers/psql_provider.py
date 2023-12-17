from asyncpg import create_pool, Record
from typing import Any, List, Optional
from loguru import logger
from configs import psql_settings, app_settings
from fastapi.encoders import jsonable_encoder


class DB:
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self) -> None:
        self._connection_pool = None

    async def connect(self) -> None:
        if self._connection_pool is None:
            self._connection_pool = await create_pool(
                dsn=psql_settings.DSN, min_size=1, max_size=10, command_timeout=60
            )

    async def fetch_one(self, query: str) -> Optional[Record]:
        if self._connection_pool is None:
            await self.connect()
        async with self._connection_pool.acquire() as con:
            if app_settings.DEBUG:
                logger.info(query)
            result = await con.fetchrow(query)
            return jsonable_encoder(result)

    async def fetch_all(self, query: str) -> List[Record]:
        if self._connection_pool is None:
            await self.connect()
        async with self._connection_pool.acquire() as con:
            if app_settings.DEBUG:
                logger.info(query)
            result = await con.fetch(query)
            return jsonable_encoder(result)

    async def fetch_value(self, query: str) -> Any:
        if self._connection_pool is None:
            await self.connect()
        async with self._connection_pool.acquire() as con:
            if app_settings.DEBUG:
                logger.info(query)
            result = await con.fetchval(query)
            return result

    async def execute(self, query: str) -> None:
        if self._connection_pool is None:
            await self.connect()
        async with self._connection_pool.acquire() as con:
            if app_settings.DEBUG:
                logger.info(query)
            await con.execute(query)

    def __del__(self) -> None:
        if self._connection_pool is not None:
            self._connection_pool.close()


async def register():
    await DB().connect()

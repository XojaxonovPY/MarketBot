import asyncio

from db import engine
from db.models import metadata


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


asyncio.run(init_models())

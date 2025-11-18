import asyncio

from db.model import db, metadata


async def init_models():
    async with db._engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


asyncio.run(init_models())

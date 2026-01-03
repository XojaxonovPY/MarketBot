# db/backup.py
import asyncio
import json
import sys
from datetime import datetime, date

from sqlalchemy import select

from db.models import Category, Product  # o'zingizdagi modellar
from db.session import AsyncSessionLocal  # db = AsyncDatabaseSession()

sys.stdout.reconfigure(encoding='utf-8')


def to_dict(obj):
    data: dict = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, (datetime, date)):
            value = value.isoformat()
        data[column.name] = value
    return data


async def create_backup(filename="db/fixtures/backup.json"):
    # Asinxron session
    async with AsyncSessionLocal() as session:
        data: dict = {}
        models: list = [Category, Product]
        for model in models:
            result = await session.execute(select(model))
            rows = result.scalars().all()
            data[model.__tablename__] = [to_dict(row) for row in rows]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("🔥 Backup created:", filename)


if __name__ == "__main__":
    asyncio.run(create_backup())

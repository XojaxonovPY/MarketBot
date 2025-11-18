# db/backup.py
import json
import asyncio
from sqlalchemy import select
from sqlalchemy.inspection import inspect
from db import db  # db = AsyncDatabaseSession()
from db.model import Category, Product  # o'zingdagi modellarni kirgiz


def to_dict(obj):
    mapper = inspect(obj).mapper
    return {column.key: getattr(obj, column.key) for column in mapper.column_attrs}


async def create_backup(filename="db/fixtures/backup.json"):
    session = db._session

    data = {}
    models = [Category, Product]

    for model in models:
        result = await session.execute(select(model))
        rows = result.scalars().all()
        data[model.__tablename__] = [to_dict(row) for row in rows]

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("🔥 Backup created:", filename)


if __name__ == "__main__":
    db.init()
    asyncio.run(create_backup())

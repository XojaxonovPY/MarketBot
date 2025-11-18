# db/restore.py
import json
import asyncio
from sqlalchemy import insert
from db import db
from db.model import Category, Product


async def load_backup(filename="db/fixtures/backup.json"):
    session = db._session

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    models = [Category, Product]

    for model in models:
        rows = data.get(model.__tablename__, [])
        for row in rows:
            await session.execute(insert(model).values(**row))

    await session.commit()

    print("🔥 Backup restored!")


if __name__ == "__main__":
    db.init()
    asyncio.run(load_backup())

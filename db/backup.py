# db/backup.py
import json
import asyncio
from datetime import datetime, date
import sys

from sqlalchemy import select
from db import db  # db = AsyncDatabaseSession()
from db.model import Category, Product  # o'zingizdagi modellar


# Konsol UTF-8 ga o'tkaziladi (Windows uchun emoji ishlashi uchun)
sys.stdout.reconfigure(encoding='utf-8')


def to_dict(obj):
    data = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, (datetime, date)):
            value = value.isoformat()  # datetime/date ni stringga aylantirish
        data[column.name] = value
    return data


async def create_backup(filename="db/fixtures/backup.json"):
    # Asinxron session
    session = db._session

    data = {}
    models = [Category, Product]

    for model in models:
        result = await session.execute(select(model))
        rows = result.scalars().all()
        data[model.__tablename__] = [to_dict(row) for row in rows]

    # JSON faylga yozish
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("🔥 Backup created:", filename)


if __name__ == "__main__":
    db.init()
    asyncio.run(create_backup())

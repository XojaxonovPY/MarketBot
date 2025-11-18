# db/restore.py
import json
import asyncio
from datetime import datetime, date
from sqlalchemy import insert
from db import db
from db.model import Category, Product
import sys

# Konsol UTF-8 ga o'tkaziladi (Windows uchun emoji ishlashi uchun)
sys.stdout.reconfigure(encoding='utf-8')


def convert_dates(row, model):
    """row dict ichidagi ISO datetime stringlarini asl datetime/date ga o'zgartirish"""
    new_row = {}
    for column in model.__table__.columns:
        value = row.get(column.name)
        if value is not None:
            col_type_str = str(column.type).upper()
            if col_type_str.startswith("DATETIME") or col_type_str.startswith("DATE"):
                if isinstance(value, str):
                    try:
                        value = datetime.fromisoformat(value)
                    except ValueError:
                        try:
                            value = date.fromisoformat(value)
                        except ValueError:
                            pass  # noto'g'ri format bo'lsa, o'zgartirmaymiz
        new_row[column.name] = value
    return new_row


async def load_backup(filename="db/fixtures/backup.json"):
    session = db._session

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    models = [Category, Product]

    for model in models:
        rows = data.get(model.__tablename__, [])
        for row in rows:
            row = convert_dates(row, model)  # datetime/date ni tiklash
            await session.execute(insert(model).values(**row))

    await session.commit()

    print("🔥 Backup restored!")


if __name__ == "__main__":
    db.init()
    asyncio.run(load_backup())

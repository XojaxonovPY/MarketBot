# db/restore.py
import asyncio
import json
import sys
from datetime import datetime, date

from sqlalchemy import insert

from db.models import Category, Product
from db.session import AsyncSessionLocal

sys.stdout.reconfigure(encoding='utf-8')


def convert_dates(row, model):
    new_row: dict = {}
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
                            pass
        new_row[column.name] = value
    return new_row


async def load_backup(filename="db/fixtures/backup.json"):
    async with AsyncSessionLocal() as session:
        with open(filename, "r", encoding="utf-8") as f:
            data: dict = json.load(f)
        models = [Category, Product]
        for model in models:
            rows = data.get(model.__tablename__, [])
            for row in rows:
                row = convert_dates(row, model)  # datetime/date ni tiklash
                await session.execute(insert(model).values(**row))
        await session.commit()
    print("🔥 Backup restored!")


if __name__ == "__main__":
    asyncio.run(load_backup())

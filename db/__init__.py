from sqlalchemy.ext.asyncio import create_async_engine

from utils.env_data import Config

engine = create_async_engine(Config.dp.DB_URL, echo=False, future=True)
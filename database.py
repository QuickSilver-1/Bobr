from gino import Gino
import sqlalchemy as sa
from typing import List
import datetime
from aiogram import Dispatcher
from config import config_1
from sqlalchemy import Column, String, sql
from asyncio import get_event_loop


db = Gino()

class BaseModel(db.Model):
    __abstract__ = True

    def __str__(self):
        model = self.__class__.__name__
        table: sa.Table = sa.inspect(self.__class__)
        primary_key_columns: List[sa.Column] = table.primary_key.columns
        values = {
            column.name: getattr(self, self._column_name_map[column.name])
            for column in primary_key_columns
        }
        values_str = " ".join(f"{name}={value!r}" for name, value in values.items())
        return f"<{model} {values_str}>"


class TimedBaseModel(BaseModel):
    __abstract__ = True

    created_at = db.Column(db.DateTime(True), server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        server_default=db.func.now())
    
async def on_start(dispatcher: Dispatcher):
    await db.set_bind(config_1.POSTGRES_URL)


class Admin(TimedBaseModel):
    __tablename__ = 'admin'

    tg_id = Column(String(100))
    first_name = Column(String(30))
    last_name = Column(String(30))

    query: sql.select

class Users(TimedBaseModel):
    __tablename__ = 'users'

    tg_id = Column(String(100), primary_key=True)
    username = Column(String(100))
    first_name = Column(String(30))
    last_name = Column(String(30))
    age = Column(String(100))

    query: sql.select


async def db_create():
    await db.set_bind(config_1.POSTGRES_URL)
    await db.gino.drop_all()
    await db.gino.create_all()

async def db_test():
    await db_create()

loop = get_event_loop()
loop.run_until_complete(db_test())
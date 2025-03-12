import os
from peewee import Model
from playhouse.db_url import connect

db = connect(os.environ.get("DATABASE_URL") or 'sqlite:///default.db') 


class BaseModel(Model):
    class Meta:
        database = db
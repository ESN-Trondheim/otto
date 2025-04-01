from peewee import CharField

from otto.persistence.database import BaseModel


class RedirectLink(BaseModel):
    id = CharField(unique=True)
    url = CharField()

    @staticmethod
    def get_url_by_id(id: str) -> str:
        return RedirectLink.get(id=id).url


RedirectLink.create_table()

from datetime import datetime

import peewee
from playhouse.sqlite_ext import JSONField

from proxyfinder.utils import PROXIES_OUT_DIR

database_path = PROXIES_OUT_DIR / "proxies.db"
db = peewee.SqliteDatabase(database_path)


class Proxy(peewee.Model):
    proxy = peewee.CharField(unique=True)
    is_working = peewee.BooleanField(default=False)
    latency = peewee.FloatField(default=0)
    is_checked = peewee.BooleanField(default=False)
    created_at = peewee.DateTimeField(default=datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.now)
    note = peewee.TextField(null=True)
    location = JSONField(null=True)
    error = peewee.TextField(null=True)

    class Meta:
        database = db

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def save_proxies(cls, proxies: list[str]) -> bool:
        existing = [i.proxy for i in Proxy.select().where(Proxy.proxy.in_(proxies))]  # type: ignore
        new_items = [Proxy(proxy=i) for i in proxies if i not in existing]
        if new_items:
            with db.atomic():
                Proxy.bulk_create(new_items)
            return True
        return False


db.connect()
db.create_tables([Proxy], safe=True)

new_columns = {
    "note": "TEXT",
    "location": "JSON",
    "error": "TEXT",
}

for column, column_type in new_columns.items():
    try:
        db.execute_sql(f"ALTER TABLE proxy ADD COLUMN {column} {column_type};")
    except peewee.OperationalError:
        pass

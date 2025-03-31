from datetime import datetime

import peewee
from playhouse.sqlite_ext import JSONField
from playhouse.shortcuts import chunked
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
    def save_proxies(cls, proxies: list[str]) -> int:
        existing = [i.proxy for i in Proxy.select().where(Proxy.proxy.in_(proxies))]  # type: ignore
        new_items = [Proxy(proxy=i) for i in proxies if i not in existing]
        if new_items:
            with db.atomic():
                for batch in chunked(new_items, 500):
                    Proxy.bulk_create(batch)
        return len(new_items)

    def to_dict(self):
        return {
            "proxy": self.proxy,
            "is_working": self.is_working,
            "latency": self.latency,
            "is_checked": self.is_checked,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M"),
            "note": self.note,
            "location": self.location,
            "error": self.error,
        }


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

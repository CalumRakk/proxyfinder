import peewee
from proxyfinder.utils import PROXIES_OUT_DIR
from datetime import datetime

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

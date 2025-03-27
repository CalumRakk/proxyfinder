import peewee
from proxyfinder.utils import PROXIES_OUT_DIR

database_path = PROXIES_OUT_DIR / "proxies.db"
database_path.parent.mkdir(parents=True, exist_ok=True)
db = peewee.SqliteDatabase(database_path)


class Proxy(peewee.Model):
    proxy = peewee.CharField(unique=True)
    is_working = peewee.BooleanField(default=False)
    latency = peewee.FloatField(default=0)
    is_checked = peewee.BooleanField(default=False)

    class Meta:
        database = db

    @classmethod
    def save_proxies(cls, proxies: list[str]) -> bool:
        ider = "proxy"
        existing = [i.proxy for i in Proxy.select().where(Proxy.proxy.in_(proxies))]  # type: ignore
        new_items = [Proxy(proxy=i) for i in proxies if i not in existing]
        if new_items:
            with db.atomic():
                Proxy.bulk_create(new_items)
            return True
        return False


db.connect()
db.create_tables([Proxy], safe=True)

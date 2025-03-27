from proxyfinder.proxyfinder import ProxyFinder
from proxyfinder.database import Proxy


def main():
    pf = ProxyFinder()
    proxies = Proxy.select().where(Proxy.is_checked == False)

    if not proxies.exists():
        proxyly = pf.get_proxies_from_multiple_sources()
        if Proxy.save_proxies(proxyly):
            proxies = Proxy.select().where(Proxy.is_checked == False)
        else:
            return
    pf.check_proxies(proxies)


if __name__ == "__main__":
    main()

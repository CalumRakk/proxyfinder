from proxyfinder import ProxyFinder
from proxyfinder.utils import save_proxies, load_proxies


def main():
    pf = ProxyFinder()
    proxies = load_proxies()
    if not proxies:
        proxies = pf.get_proxies_from_multiple_sources()
        save_proxies(proxies)
    pf.check_proxies(proxies)


if __name__ == "__main__":
    main()

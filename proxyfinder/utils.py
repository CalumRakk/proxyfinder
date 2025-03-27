from pathlib import Path
import csv
import random
import os
import re

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]
PROXIES_OUT_DIR = Path(os.getenv("APPDATA") or Path.home() / ".config") / "proxyfinder"

REGEX_GET_PROXY = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5})")


def get_user_agent() -> str:
    return random.choice(USER_AGENTS)


def load_proxies() -> list[str]:
    path = PROXIES_OUT_DIR / "proxies.txt"
    if path.exists():
        return path.read_text().splitlines()
    return []


def save_proxies(proxies: list[str]):
    PROXIES_OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = PROXIES_OUT_DIR / "proxies.txt"
    path.write_text("\n".join(proxies))

    print("Proxies guardados en proxies.txt")

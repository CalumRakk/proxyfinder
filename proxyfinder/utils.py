from pathlib import Path
import threading
import random
import os
import re
import logging

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]
PROXIES_OUT_DIR = Path(os.getenv("APPDATA") or Path.home() / ".config") / "proxyfinder"
PROXIES_OUT_DIR.mkdir(parents=True, exist_ok=True)
REGEX_GET_PROXY = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5})")
TEST_URLS = ["https://www.example.com", "https://httpbin.org/ip"]
STOP_FLAG = threading.Event()


def handler_stream(formatter) -> "logging.StreamHandler":
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    return console_handler


def handler_file(path, formatter) -> "logging.FileHandler":
    file_handler = logging.FileHandler(str(path), encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    return file_handler


def logger_formatter() -> "logging.Formatter":
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%d-%m-%Y %I:%M:%S %p",
    )
    return formatter


def get_user_agent() -> str:
    return random.choice(USER_AGENTS)


def signal_handler(sig, frame):
    """Maneja la señal SIGINT (Ctrl+C)."""
    logging.info("Señal SIGINT recibida. Deteniendo...")
    STOP_FLAG.set()

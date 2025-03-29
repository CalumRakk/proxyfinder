import logging
import os
import threading
from pathlib import Path


PROXIES_OUT_DIR = Path(os.getenv("APPDATA") or Path.home() / ".config") / "proxyfinder"
PROXIES_OUT_DIR.mkdir(parents=True, exist_ok=True)
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


def signal_handler(sig, frame):
    """Maneja la señal SIGINT (Ctrl+C)."""
    logging.info("SIGINT signal received. Stopping...")
    STOP_FLAG.set()

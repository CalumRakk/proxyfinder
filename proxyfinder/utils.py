import logging
import os
import threading
from pathlib import Path
import curses


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
    logging.info("SIGINT signal received. Please wait... closing threads...")
    STOP_FLAG.set()


class ProxyDisplay:
    def __init__(self, stdscr: curses.window, proxies):
        self.stdscr = stdscr
        self.proxies = list(proxies)
        self.bottom_message_space = 2
        self.max_visible_proxies = curses.LINES - self.bottom_message_space
        self.start_index = 0
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

    def display_proxies(self):
        self.stdscr.clear()

        end = min(self.start_index + self.max_visible_proxies, len(self.proxies))
        visible_proxies = self.proxies[self.start_index : end]

        for i, proxy in enumerate(visible_proxies):
            line = f"{proxy.proxy} - Working: {proxy.is_working} - Latency: {proxy.latency} ms - updated: {proxy.updated_at.strftime('%Y-%m-%d %H:%M')}"
            if proxy.is_working:
                self.stdscr.addstr(i, 0, line, curses.color_pair(1))
            else:
                self.stdscr.addstr(i, 0, line)

        self.stdscr.addstr(
            self.max_visible_proxies + 1,
            0,
            f"({end}/{len(self.proxies)}) Press q to quit, j/k to scroll",
        )
        self.stdscr.refresh()

    def navigate(self):
        self.display_proxies()

        while True:
            key = self.stdscr.getch()

            if key == ord("q"):
                break
            elif key == ord("j"):  # Flecha abajo
                if self.start_index + self.max_visible_proxies < len(self.proxies):
                    self.start_index += 1
                    self.display_proxies()
            elif key == ord("k"):  # Flecha arriba
                if self.start_index > 0:
                    self.start_index -= 1
                    self.display_proxies()

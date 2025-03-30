import argparse
import csv
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path

from peewee import fn

from proxyfinder.database import Proxy
from proxyfinder.proxyfinder import ProxyFinder
from proxyfinder.utils import signal_handler, ProxyDisplay

from curses import wrapper, window


def config_args():
    parser = argparse.ArgumentParser(description="Finds and verifies HTTP proxies.")
    parser.add_argument(
        "action",
        nargs="?",
        choices=["check", "export", "show"],
        default="check",
        help="Action to perform: 'check' to verify proxies, 'export' to export proxies to a CSV file.",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default="proxies.csv",
        help="Location of the CSV file to export proxies to (default: proxies.csv).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export all proxies (default: only working proxies).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit the number of proxies to check (default: 300).",
    )
    return parser.parse_args(["show", "--limit", "50"])


def show_proxies(stdscr: window, working_only=True, limit=None):
    proxies = Proxy.select()
    if working_only:
        proxies = proxies.where(Proxy.is_working == working_only)

    if limit:
        proxies = proxies.limit(limit)

    display = ProxyDisplay(stdscr, proxies)
    display.navigate()


def ckeck_proxies():
    with ProxyFinder() as pf:
        a_day_ago = datetime.now() - Proxy.updated_at  # type: ignore
        proxies = Proxy.select().where(
            (Proxy.is_checked == False) | ((Proxy.is_working == True) & (Proxy.updated_at > a_day_ago))  # type: ignore
        )

        if not proxies.exists():
            logging.info("No proxies found, getting proxies from multiple sources.")
            nuevos_proxies = pf.get_proxies_from_multiple_sources()
            if not Proxy.save_proxies(nuevos_proxies):
                return
            proxies = Proxy.select().where(Proxy.is_checked == False)

        pf.check_proxies(proxies)

    latency_mean = Proxy.select(fn.AVG(Proxy.latency)).where(Proxy.is_working == True).scalar()  # type: ignore
    latency_mean = round(latency_mean, 2)
    proxies_working = Proxy.select().where(Proxy.is_working == True)  # type: ignore
    logging.info(
        f"Proxies working: {len(proxies_working)}, latency mean: {latency_mean} ms"
    )


def export_proxies(output, all_proxies):
    logging.info(f"Exporting proxies to {output}, including all: {all_proxies}")
    proxies = (
        Proxy.select()
        if all_proxies
        else Proxy.select().where(Proxy.is_working == True)
    )

    output = Path(output).with_suffix(".csv")
    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "proxy",
                "is_working",
                "latency",
                "is_checked",
                "created_at",
                "updated_at",
                "note",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for proxy in proxies:
                writer.writerow(
                    {
                        "proxy": proxy.proxy,
                        "is_working": proxy.is_working,
                        "latency": proxy.latency,
                        "is_checked": proxy.is_checked,
                        "created_at": proxy.created_at,
                        "updated_at": proxy.updated_at,
                        "note": proxy.note,
                    }
                )
        logging.info(f"Proxies successfully exported to {output}")
    except Exception as e:
        logging.error(f"Error exporting proxies: {e}")


def main(stdscr):
    signal.signal(signal.SIGINT, signal_handler)
    args = config_args()

    try:
        if args.action == "check":
            ckeck_proxies()
        elif args.action == "export":
            export_proxies(args.output, args.all)
        elif args.action == "show":
            show_proxies(stdscr, working_only=False, limit=args.limit)
    except KeyboardInterrupt:
        logging.info("Process interrupted by user.")
        sys.exit(0)


if __name__ == "__main__":
    wrapper(main)

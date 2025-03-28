import argparse
import csv
import logging
import signal
import sys
from pathlib import Path

from proxyfinder.database import Proxy
from proxyfinder.proxyfinder import ProxyFinder
from proxyfinder.utils import signal_handler


def config_args():
    parser = argparse.ArgumentParser(description="Finds and verifies HTTP proxies.")
    parser.add_argument(
        "action",
        nargs="?",
        choices=["check", "export"],
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
    return parser.parse_args()


def ckeck_proxies():
    pf = ProxyFinder()
    proxies = Proxy.select().where(Proxy.is_checked == False)

    if not proxies.exists():
        logging.info("No proxies found, getting proxies from multiple sources.")
        nuevos_proxies = pf.get_proxies_from_multiple_sources()
        if not Proxy.save_proxies(nuevos_proxies):
            return
        proxies = Proxy.select().where(Proxy.is_checked == False)

    pf.check_proxies(proxies)


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


def main():
    signal.signal(signal.SIGINT, signal_handler)
    args = config_args()

    try:
        if args.action == "check":
            ckeck_proxies()
        elif args.action == "export":
            export_proxies(args.output, args.all)
    except KeyboardInterrupt:
        logging.info("Process interrupted by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()

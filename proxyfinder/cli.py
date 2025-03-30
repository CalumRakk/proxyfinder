import argparse
from datetime import datetime
from proxyfinder.database import Proxy
from proxyfinder.proxyfinder import ProxyFinder
from proxyfinder.utils import ProxyDisplay
from datetime import timedelta
import logging
from pathlib import Path
import csv
import signal
from curses import wrapper
import sys
from proxyfinder.utils import signal_handler
from peewee import fn
import os

logger = logging.getLogger(__name__)


def config_args():
    parser = argparse.ArgumentParser(
        description="CLI to find, check, and manage HTTP proxies."
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    # 'find' command
    find_parser = subparsers.add_parser("find", help="Find new proxies.")
    find_parser.add_argument(
        "--concurrency", type=int, default=10, help="Number of threads for searching."
    )

    # 'check' command
    check_parser = subparsers.add_parser("check", help="Check the status of proxies.")
    check_parser.add_argument(
        "--status",
        choices=["working", "broken", "unchecked", "all"],
        default="working",
        help="Filter proxies by status.",
    )
    check_parser.add_argument(
        "--concurrency", type=int, default=10, help="Number of threads for checking."
    )
    check_parser.add_argument(
        "--older-than",
        type=int,
        default=0,
        help="Only check proxies older than N days.",
    )

    # 'show' command
    show_parser = subparsers.add_parser("show", help="Display stored proxies.")
    show_parser.add_argument(
        "--status",
        choices=["working", "broken", "unchecked", "all"],
        default="working",
        help="Filter proxies by status.",
    )
    show_parser.add_argument(
        "--limit", type=int, help="Limit the number of proxies to display."
    )
    show_parser.add_argument(
        "--count",
        action="store_true",
        help="Show the number of proxies in the database.",
    )
    show_parser.add_argument(
        "--sort-by",
        choices=["latency", "created_at", "updated_at"],
        default="latency",
        help="Sort proxies by a specific field.",
    )
    show_parser.add_argument(
        "--reverse", action="store_true", help="Reverse the order of proxies."
    )
    show_parser.add_argument(
        "--older-than", type=int, default=0, help="Filter proxies older than N days."
    )

    # 'export' command
    export_parser = subparsers.add_parser(
        "export", help="Export proxies to a CSV file."
    )
    export_parser.add_argument("output", type=str, help="Output file.")
    export_parser.add_argument(
        "--all", action="store_true", help="Export all proxies, not just working ones."
    )

    # 'update' command
    update_parser = subparsers.add_parser("update", help="Find and check new proxies.")
    update_parser.add_argument(
        "--concurrency", type=int, default=10, help="Number of threads for updating."
    )

    args = parser.parse_args()
    if hasattr(args, "concurrency"):
        concurrency = os.cpu_count() or 2
        concurrency += 2
        max_concurrency = min(concurrency, args.concurrency)
        setattr(args, "concurrency", max_concurrency)
    return args


def show_proxies(
    status: str, limit=None, count=False, sort_by="latency", reverse=False, older_than=0
):
    if status == "working":
        proxies = Proxy.select().where(
            Proxy.is_working == True, Proxy.is_checked == True
        )
    elif status == "broken":
        proxies = Proxy.select().where(
            Proxy.is_working == False, Proxy.is_checked == True
        )
    elif status == "unchecked":
        proxies = Proxy.select().where(Proxy.is_checked == False)
    elif status == "all":
        proxies = Proxy.select()
    else:
        raise ValueError(f"Invalid status: {status}")

    if limit:
        proxies = proxies.limit(limit)

    if older_than > 0 and status != "all":
        a_day_ago = datetime.now() - timedelta(days=older_than)
        proxies = proxies.where(Proxy.updated_at > a_day_ago)  # type: ignore

    if count:
        print(
            f"Total proxies: {len(proxies)}{f' {status}' if status != 'all' else ''} in the database"
        )
        return

    proxies = sorted(proxies, key=lambda x: getattr(x, sort_by), reverse=reverse)

    def func(stdscr):
        display = ProxyDisplay(stdscr, proxies)
        display.navigate()

    wrapper(func)


def ckeck_proxies(concurrency, status="working", older_than=0):
    with ProxyFinder(concurrency=concurrency) as pf:

        if status == "working":
            proxies = Proxy.select().where(
                Proxy.is_working == True,
                Proxy.is_checked == True,
            )
        elif status == "broken":
            proxies = Proxy.select().where(
                Proxy.is_working == False, Proxy.is_checked == True
            )
        elif status == "unchecked":
            proxies = Proxy.select().where(Proxy.is_checked == False)
        elif status == "all":
            proxies = Proxy.select()
        else:
            raise ValueError(f"Invalid status: {status}")

        if older_than > 0:
            a_day_ago = datetime.now() - timedelta(days=older_than)
            proxies = proxies.where(Proxy.updated_at > a_day_ago)  # type: ignore

        pf.check_proxies(proxies)

    # latency_mean = Proxy.select(fn.AVG(Proxy.latency)).where(Proxy.is_working == True).scalar()  # type: ignore
    # latency_mean = round(latency_mean, 2)
    # proxies_working = Proxy.select().where(Proxy.is_working == True)  # type: ignore
    # logging.info(
    #     f"Proxies working: {len(proxies_working)}, latency mean: {latency_mean} ms"
    # )


def find_proxies(concurrency):
    with ProxyFinder(concurrency=concurrency) as pf:
        news_proxies = pf.get_proxies_from_multiple_sources()
        count_new_proxies = Proxy.save_proxies(news_proxies)
        logging.info(f"Obtained {count_new_proxies} new proxies from multiple sources.")


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


def update_proxies(concurrency):
    find_proxies(concurrency=concurrency)
    ckeck_proxies(concurrency=concurrency)


def main():
    signal.signal(signal.SIGINT, signal_handler)

    args = config_args()

    try:
        logger.debug(f"Action: {args.action} args: {args}")
        if args.action == "check":
            ckeck_proxies(
                concurrency=args.concurrency,
                status=args.status,
                older_than=args.older_than,
            )
        elif args.action == "export":
            export_proxies(args.output, args.all)
        elif args.action == "find":
            find_proxies(concurrency=args.concurrency)
        elif args.action == "update":
            update_proxies(concurrency=args.concurrency)
        elif args.action == "show":
            show_proxies(
                status=args.status,
                limit=args.limit,
                count=args.count,
                sort_by=args.sort_by,
                reverse=args.reverse,
                older_than=args.older_than,
            )

    except KeyboardInterrupt:
        logging.info("Proceso interrumpido por el usuario.")
        sys.exit(0)


if __name__ == "__main__":
    main()

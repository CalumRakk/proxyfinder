import argparse
from proxyfinder.proxyfinder import ProxyFinder
from proxyfinder.database import Proxy
import csv
import logging
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Encuentra y verifica proxies HTTP.")
    parser.add_argument(
        "action",
        nargs="?",
        choices=["check", "export"],
        help="Acción a realizar: 'check' para verificar proxies, 'export' para exportar proxies a un archivo CSV.",
        default="check",
    )
    parser.add_argument(
        "ubicacion",
        nargs="?",
        default="proxies.csv",
        help="Ubicación del archivo CSV para exportar los proxies (por defecto: proxies.csv).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Exportar todos los proxies (por defecto: solo los proxies funcionales).",
    )
    args = parser.parse_args()

    pf = ProxyFinder()

    if args.action == "check":
        try:
            proxies = Proxy.select().where(Proxy.is_checked == False)

            if not proxies.exists():
                proxyly = pf.get_proxies_from_multiple_sources()
                if Proxy.save_proxies(proxyly):
                    proxies = Proxy.select().where(Proxy.is_checked == False)
                else:
                    return
            pf.check_proxies(proxies)
        except KeyboardInterrupt:
            logging.info("Proceso interrumpido por el usuario.")
            sys.exit(0)

    elif args.action == "export":
        export_proxies(args.ubicacion, args.all)


def export_proxies(ubicacion, all_proxies):
    logging.info(f"Exportando proxies a {ubicacion}, incluir todos: {all_proxies}")
    if all_proxies:
        proxies = Proxy.select()
    else:
        proxies = Proxy.select().where(Proxy.is_working == True)

    ubicacion = Path(ubicacion) if isinstance(ubicacion, str) else ubicacion
    ubicacion = (
        ubicacion if ubicacion.suffix == ".csv" else ubicacion.with_suffix(".csv")
    )
    ubicacion.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(ubicacion, "w", newline="", encoding="utf-8") as csvfile:
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
        logging.info(f"Proxies exportados exitosamente a {ubicacion}")
    except Exception as e:
        logging.error(f"Error al exportar proxies: {e}")


if __name__ == "__main__":
    main()

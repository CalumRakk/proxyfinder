import requests
from concurrent.futures import ThreadPoolExecutor
import time
from bs4 import BeautifulSoup, Tag
from proxyfinder.utils import get_user_agent, REGEX_GET_PROXY, TEST_URLS, STOP_FLAG
from typing import Union, List
import json
import importlib.resources
from proxyfinder.database import Proxy
import logging
import random
from datetime import datetime


class ProxyFinder:
    TIMEOUT = 5
    MAX_WORKERS = 50
    THREAD_POOL_SIZE = 10

    def __init__(self):
        self.session = requests.Session()
        logging.info("ProxyFinder inicializado.")

    def fetch_proxies_from_source(
        self, url: str, parser_type: str = "table"
    ) -> List[str]:
        """
        Obtiene proxies de una fuente específica.
        """
        logging.info(f"Obteniendo proxies de: {url} (tipo: {parser_type})")
        headers = {"User-Agent": get_user_agent()}

        try:
            response = requests.get(url, headers=headers, timeout=self.TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error al obtener proxies de {url}: {e}")
            return []

        proxies = self._parse_proxies(response.text, parser_type)
        proxies_cleaned = [
            match.group()
            for proxy in proxies
            if (match := REGEX_GET_PROXY.match(proxy))
        ]
        logging.info(f"Obtenidos {len(proxies_cleaned)} proxies limpios de {url}")
        return proxies_cleaned

    def _parse_proxies(self, content: str, parser_type: str) -> List[str]:
        """Parsea los proxies dependiendo del tipo de fuente."""
        proxies = []
        if parser_type == "table":
            soup = BeautifulSoup(content, "html.parser")
            table = soup.find("table")
            if isinstance(table, Tag):
                rows = table.find_all("tr")[1:]
                for row in rows:
                    if (
                        isinstance(row, Tag)
                        and (cols := row.find_all("td"))
                        and len(cols) >= 2
                    ):
                        proxies.append(f"{cols[0].text.strip()}:{cols[1].text.strip()}")
        elif parser_type == "plain":
            proxies = [
                line.strip()
                for line in content.split("\n")
                if ":" in line and "." in line.split(":")[0]
            ]
        return proxies

    def get_proxies_from_multiple_sources(self) -> List[str]:
        """
        Obtiene proxies de múltiples fuentes públicas.
        """
        logging.info("Obteniendo proxies de múltiples fuentes.")
        try:
            with importlib.resources.open_text("proxyfinder", "sources.json") as f:
                sources = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error al cargar sources.json: {e}")
            return []

        all_proxies = []
        with ThreadPoolExecutor(max_workers=self.THREAD_POOL_SIZE) as executor:
            futures = {
                executor.submit(self.fetch_proxies_from_source, **source): source["url"]
                for source in sources
            }
            for future in futures:
                try:
                    proxies = future.result()
                    all_proxies.extend(proxies)
                    logging.info(
                        f"Obtenidos {len(proxies)} proxies de {futures[future]}"
                    )
                except Exception as e:
                    logging.error(f"Error en fuente {futures[future]}: {e}")

        unique_proxies = list(set(all_proxies))
        logging.info(f"Total de proxies únicos obtenidos: {len(unique_proxies)}")
        return unique_proxies

    def check_proxy(self, proxy: Proxy) -> Union[Proxy, None]:
        """
        Verifica si un proxy es funcional.
        """
        if STOP_FLAG.is_set():
            return None

        logging.debug(f"Verificando proxy: {proxy.proxy}")
        proxies = {"http": f"http://{proxy.proxy}", "https": f"http://{proxy.proxy}"}
        headers = {"User-Agent": get_user_agent()}
        test_url = random.choice(TEST_URLS)

        try:
            start_time = time.time()
            proxy.is_checked = True  # type: ignore
            proxy.updated_at = datetime.now()
            response = self.session.head(
                test_url, proxies=proxies, headers=headers, timeout=self.TIMEOUT
            )
            response.raise_for_status()
            proxy.latency = round((time.time() - start_time) * 1000, 2)  # type: ignore
            proxy.is_working = True  # type: ignore
            logging.info(
                f"Proxy {proxy.proxy} funciona ({proxy.latency} ms) estado: {response.status_code}"
            )
            return proxy
        except requests.RequestException:
            proxy.is_working = False  # type: ignore
            logging.debug(f"Proxy {proxy.proxy} falló la conexión.")
            return proxy

    def check_proxies(self, proxies: List[Proxy]):
        """
        Verifica una lista de proxies en paralelo.
        """
        logging.info(f"Verificando {len(proxies)} proxies.")
        to_save = []

        with ThreadPoolExecutor(max_workers=self.THREAD_POOL_SIZE) as executor:
            futures = {
                executor.submit(self.check_proxy, proxy): proxy for proxy in proxies
            }

            for index, future in enumerate(futures, 1):
                proxy = future.result()
                if proxy is None:
                    continue
                logging.info(f"Procesado proxy {index}/{len(futures)}")
                if proxy:
                    to_save.append(proxy)

                if index % 10 == 0 and to_save:
                    Proxy.bulk_update(
                        to_save, ["is_checked", "is_working", "latency", "updated_at"]
                    )
                    logging.info(
                        f"Actualizados {len(to_save)} proxies en la base de datos."
                    )
                    to_save.clear()

        if to_save:
            Proxy.bulk_update(
                to_save, ["is_checked", "is_working", "latency", "updated_at"]
            )
            logging.info(
                f"Actualizados {len(to_save)} proxies restantes en la base de datos."
            )

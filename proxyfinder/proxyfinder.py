import requests
from concurrent.futures import ThreadPoolExecutor
import time
from bs4 import BeautifulSoup, Tag
from proxyfinder.utils import get_user_agent, REGEX_GET_PROXY, TEST_URLS, STOP_FLAG
from typing import Union
import json
import importlib.resources
from proxyfinder.database import Proxy
import logging
import random
from datetime import datetime
import threading


class ProxyFinder:
    def __init__(self):
        self.timeout = 5
        self.max_workers = 50
        self.session = requests.Session()
        logging.info("ProxyFinder inicializado.")

    def fetch_proxies_from_source(
        self, url: str, parser_type: str = "table"
    ) -> list[str]:
        """
        Obtiene proxies de una fuente específica
        :param url: URL de la fuente
        :param parser_type: 'table' para tablas HTML, 'plain' para texto plano
        :return: lista de proxies (ip:puerto)
        """
        logging.info(f"Obteniendo proxies de la fuente: {url} (tipo: {parser_type})")
        try:
            headers = {"User-Agent": get_user_agent()}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            logging.debug(f"Respuesta de {url}: {response.status_code}")

            proxies = []

            if parser_type == "table":
                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find("table")
                if isinstance(table, Tag):
                    rows = table.find_all("tr")
                    for row in rows[1:]:
                        if isinstance(row, Tag):
                            cols = row.find_all("td")
                            if len(cols) >= 2:
                                ip = cols[0].text.strip()
                                port = cols[1].text.strip()
                                proxies.append(f"{ip}:{port}")

            elif parser_type == "plain":
                for line in response.text.split("\n"):
                    line = line.strip()
                    if ":" in line and "." in line.split(":")[0]:
                        proxies.append(line)

            proxies_cleaned = []
            for proxy in proxies:
                match = REGEX_GET_PROXY.match(proxy)
                if match:
                    proxies_cleaned.append(match.group())
            logging.info(f"Obtenidos {len(proxies_cleaned)} proxies limpios de {url}")
            return proxies_cleaned

        except Exception as e:
            logging.error(f"Error al obtener proxies de {url}: {str(e)}")
            return []

    def get_proxies_from_multiple_sources(self) -> list[str]:
        """
        Obtiene proxies de múltiples fuentes públicas

        :return: lista de proxies únicos

        Ejemplo de respuesta:
        [
            "54.212.22.168:3128",
            "35.193.125.123:80",
            ...
        ]
        """
        logging.info("Obteniendo proxies de múltiples fuentes.")
        try:
            with importlib.resources.open_text("proxyfinder", "sources.json") as f:
                sources = json.load(f)
            logging.debug(f"Fuentes cargadas: {sources}")
        except FileNotFoundError as e:
            logging.error(f"No se pudo encontrar el archivo sources.json: {e}")
            return []
        except json.JSONDecodeError as e:
            logging.error(f"Error al decodificar JSON en sources.json: {e}")
            return []

        all_proxies = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for source in sources:
                futures.append(
                    executor.submit(self.fetch_proxies_from_source, **source)
                )

            for future in futures:
                try:
                    proxies = future.result()
                    all_proxies.extend(proxies)
                    logging.info(f"Obtenidos {len(proxies)} proxies de {source['url']}")
                except Exception as e:
                    logging.error(f"Error al procesar fuente: {str(e)}")

        # Eliminar duplicados
        unique_proxies = list(set(all_proxies))
        logging.info(f"Total de proxies únicos obtenidos: {len(unique_proxies)}")
        return unique_proxies

    def check_proxy(self, proxy: Proxy) -> Union[Proxy, None]:
        """
        Verifica si un proxy es funcional
        :param proxy: dirección del proxy (ip:puerto)
        :return: tupla (proxy, tiempo_respuesta, funciona) o None si hay error
        """
        if STOP_FLAG.is_set():
            return
        logging.debug(f"Verificando proxy: {proxy.proxy}")
        test_url = random.choice(TEST_URLS)
        proxies = {
            "http": f"http://{proxy.proxy}",
            "https": f"http://{proxy.proxy}",
        }

        try:
            headers = {"User-Agent": get_user_agent()}
            start_time = time.time()
            proxy.is_checked = True  # type: ignore
            proxy.updated_at = datetime.now()
            response = self.session.head(
                test_url, proxies=proxies, headers=headers, timeout=self.timeout
            )
            end_time = time.time()
            response.raise_for_status()
            proxy.latency = round((end_time - start_time) * 1000, 2)  # type: ignore
            proxy.is_working = True  # type: ignore
            logging.info(
                f"Proxy {proxy.proxy} funciona ({proxy.latency} ms) estado: {response.status_code}"
            )
            return proxy

        except requests.exceptions.RequestException as e:
            proxy.is_working = False  # type: ignore
            logging.debug(f"Proxy {proxy.proxy} falló la conexión: {e}")
            return proxy

    def check_proxies(self, proxies: list[Proxy]):
        logging.info(f"Verificando {len(proxies)} proxies.")
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for proxy in proxies:
                futures.append(executor.submit(self.check_proxy, proxy))

            try:
                cout_futures = len(futures)
                to_save = []
                for index, future in enumerate(futures, 1):
                    logging.info(f"Procesando proxy {index}/{cout_futures}")
                    proxy = future.result()
                    to_save.append(proxy)
                    if index % 10 == 0:
                        Proxy.bulk_update(
                            to_save,
                            [
                                "is_checked",
                                "is_working",
                                "latency",
                                "updated_at",
                            ],
                        )
                        logging.info(
                            f"Actualizados {len(to_save)} proxies en la base de datos."
                        )
                        to_save = []

            except Exception as e:
                logging.debug(f"Error al procesar el proxy: {str(e)}")

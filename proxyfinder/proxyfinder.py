import requests
from concurrent.futures import ThreadPoolExecutor
import time
from bs4 import BeautifulSoup, Tag
from .utils import get_user_agent, REGEX_GET_PROXY
from pathlib import Path
import json
import csv


class ProxyFinder:
    def __init__(self):
        self.timeout = 5
        self.max_workers = 50
        self.session = requests.Session()

    def fetch_proxies_from_source(
        self, url: str, parser_type: str = "table"
    ) -> list[str]:
        """
        Obtiene proxies de una fuente específica
        :param url: URL de la fuente
        :param parser_type: 'table' para tablas HTML, 'plain' para texto plano
        :return: lista de proxies (ip:puerto)
        """
        try:
            headers = {"User-Agent": get_user_agent()}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

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
            return proxies_cleaned

        except Exception as e:
            print(f"Error al obtener proxies de {url}: {str(e)}")
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

        sources = json.loads(Path("sources.json").read_text())
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
                    print(f"Obtenidos {len(proxies)} proxies de {source['url']}")
                except Exception as e:
                    print(f"Error al procesar fuente: {str(e)}")

        # Eliminar duplicados
        unique_proxies = list(set(all_proxies))
        print(f"\nTotal de proxies únicos obtenidos: {len(unique_proxies)}")
        return unique_proxies

    def check_proxy(self, proxy):
        """
        Verifica si un proxy es funcional
        :param proxy: dirección del proxy (ip:puerto)
        :return: tupla (proxy, tiempo_respuesta, funciona) o None si hay error
        """
        test_url = "http://www.google.com"  # URL para probar el proxy
        proxy = REGEX_GET_PROXY.match(proxy)
        if proxy is None:
            return None
        proxy = proxy.group()

        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }

        try:
            headers = {"User-Agent": get_user_agent()}
            start_time = time.time()
            response = self.session.get(
                test_url, proxies=proxies, headers=headers, timeout=self.timeout
            )
            end_time = time.time()

            if response.status_code == 200:
                latency = round((end_time - start_time) * 1000, 2)  # en milisegundos
                return (proxy, latency, True)

        except requests.exceptions.RequestException:
            pass

        return None

    def check_proxies(self, proxies):
        path_cvs = Path("valid_proxies.csv")
        is_new_path_cvs = not path_cvs.exists() or path_cvs.stat().st_size == 0
        proxies_checked = []
        with path_cvs.open("a+", newline="", buffering=1) as csvfile:
            csvwriter = csv.writer(csvfile)
            if is_new_path_cvs:
                csvwriter.writerow(["Proxy", "Latencia (ms)", "Funciona"])
            else:
                reader = csv.DictReader(csvfile)
                proxies_checked = [row["Proxy"].strip() for row in reader]

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for proxy in proxies:
                    if proxy in proxies_checked:
                        continue
                    futures.append(executor.submit(self.check_proxy, proxy))

                for future in futures:
                    try:
                        result = future.result()
                        if result:
                            csvwriter.writerow(result)
                            print(f"Proxy {result[0]} funcionando ({result[1]} ms)")
                    except Exception as e:
                        print(f"Error al procesar : {str(e)}")

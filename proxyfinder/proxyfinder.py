import importlib.resources
import json
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List, Union

import requests
from bs4 import BeautifulSoup, Tag

from proxyfinder.database import Proxy
from proxyfinder.utils import (
    REGEX_GET_HTTP_ERROR,
    REGEX_GET_PROXY,
    STOP_FLAG,
    TEST_URLS,
    get_user_agent,
)


class ProxyFinder:
    TIMEOUT = 5
    MAX_WORKERS = 50
    THREAD_POOL_SIZE = 10

    def __init__(self):
        self.session = requests.Session()
        logging.info("ProxyFinder initialized.")

    def fetch_proxies_from_source(
        self, url: str, parser_type: str = "table"
    ) -> List[str]:
        """
        Obtains proxies from a specific source.
        """
        logging.info(f"Fetching proxies from: {url} (type: {parser_type})")
        headers = headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,es-CO;q=0.5",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": get_user_agent(),
        }

        try:
            response = requests.get(url, headers=headers, timeout=self.TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error fetching proxies from {url}: {e}")
            return []

        proxies = self._parse_proxies(response.text, parser_type)
        proxies_cleaned = [
            match.group()
            for proxy in proxies
            if (match := REGEX_GET_PROXY.match(proxy))
        ]
        logging.info(f"Obtained {len(proxies_cleaned)} cleaned proxies from {url}")
        return proxies_cleaned

    def _parse_proxies(self, content: str, parser_type: str) -> List[str]:
        """Parses proxies depending on the source type."""
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
        Obtains proxies from multiple public sources.
        """
        logging.info("Fetching proxies from multiple sources.")
        try:
            with importlib.resources.open_text("proxyfinder", "sources.json") as f:
                sources = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error loading sources.json: {e}")
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
                        f"Obtained {len(proxies)} proxies from {futures[future]}"
                    )
                except Exception as e:
                    logging.error(f"Error in source {futures[future]}: {e}")

        unique_proxies = list(set(all_proxies))
        logging.info(f"Total unique proxies obtained: {len(unique_proxies)}")
        return unique_proxies

    def check_proxy(self, proxy: Proxy) -> Union[Proxy, None]:
        """
        Verifies if a proxy is functional.
        """
        if STOP_FLAG.is_set():
            return None

        logging.debug(f"Checking proxy: {proxy.proxy}")
        proxies = {"http": f"http://{proxy.proxy}", "https": f"http://{proxy.proxy}"}
        headers = {"User-Agent": get_user_agent()}
        test_url = random.choice(TEST_URLS)

        try:
            start_time = time.time()
            proxy.is_checked = True  # type: ignore
            proxy.updated_at = datetime.now()
            response = self.session.get(
                test_url, proxies=proxies, headers=headers, timeout=self.TIMEOUT
            )
            response.raise_for_status()
            proxy.latency = round((time.time() - start_time) * 1000, 2)  # type: ignore
            proxy.is_working = True  # type: ignore
            proxy.location = response.json()
            logging.info(
                f"Proxy {proxy.proxy} is working ({proxy.latency} ms) status: {response.status_code}"
            )

            return proxy
        except requests.RequestException as e:
            proxy.is_working = False  # type: ignore
            match = REGEX_GET_HTTP_ERROR.search(str(e))
            if match:
                proxy.error = match.group(1)
            logging.debug(f"Proxy {proxy.proxy} connection failed.")
            return proxy

    def check_proxies(self, proxies: List[Proxy]):
        """
        Verifies a list of proxies in parallel.
        """
        logging.info(f"Checking {len(proxies)} proxies.")
        to_save = []

        with ThreadPoolExecutor(max_workers=self.THREAD_POOL_SIZE) as executor:
            futures = {
                executor.submit(self.check_proxy, proxy): proxy for proxy in proxies
            }

            for index, future in enumerate(futures, 1):
                proxy = future.result()
                if proxy is None:
                    continue
                logging.info(f"Processed proxy {index}/{len(futures)}")
                if proxy:
                    to_save.append(proxy)

                if index % 10 == 0 and to_save:
                    Proxy.bulk_update(
                        to_save,
                        [
                            "is_checked",
                            "is_working",
                            "latency",
                            "updated_at",
                            "location",
                            "error",
                        ],
                    )
                    logging.info(f"Updated {len(to_save)} proxies in the database.")
                    to_save.clear()

        if to_save:
            Proxy.bulk_update(
                to_save, ["is_checked", "is_working", "latency", "updated_at"]
            )
            logging.info(f"Updated {len(to_save)} remaining proxies in the database.")

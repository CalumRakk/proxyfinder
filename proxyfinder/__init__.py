import logging
from pathlib import Path
from .utils import logger_formatter, handler_stream, handler_file, PROXIES_OUT_DIR

formatter = logger_formatter()
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        handler_stream(formatter),
        handler_file(PROXIES_OUT_DIR / "proxyfinder.log", formatter),
    ],
)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("peewee").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)
logger.info(
    """
    =====================
    Start of the program
    ====================="""
)

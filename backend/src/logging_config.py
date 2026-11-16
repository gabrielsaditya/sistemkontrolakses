
import logging
import colorlog
from enum import StrEnum

"""
KONFIGURASI LOGGING UNTUK MEMUDAHKAN DEBUGGING 
"""

class LogLevel(StrEnum):
    INFO = "INFO"
    WARN = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


FORMAT_LOG = (
    "%(log_color)s%(asctime)s - %(levelname)s - "
    "%(name)s - %(message)s%(reset)s"
)

WARNA_LOG = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}


def konfigurasi_logging(log_level: LogLevel = LogLevel.INFO):
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            FORMAT_LOG,
            log_colors=WARNA_LOG,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    logging.basicConfig(
        level=log_level.value,
        handlers=[handler],
        force=True,
    )

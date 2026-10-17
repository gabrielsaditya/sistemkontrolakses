import logging
from enum import StrEnum

class LogLevel(StrEnum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"


FORMAT_LOG = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

def konfigurasi_logging(log_level: str = LogLevel.error):
    log_level = str(log_level).upper()
    log_levels = [level.value for level in LogLevel]

    if log_level not in log_levels:
        logging.basicConfig(level=LogLevel.error)

    if log_level == LogLevel.debug:
        logging.basicConfig(level=log_level, format=FORMAT_LOG)

    logging.basicConfig(level=log_level)



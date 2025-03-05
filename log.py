import sys
import logging
import logging.handlers

root_logger = logging.getLogger()
root_logger.handlers.clear()

logger = logging.getLogger("ployquant")
logger.setLevel(logging.DEBUG)
logger.handlers.clear()

rh_formatter = logging.Formatter(
    "%(asctime)s - %(module)s - %(levelname)s - %(message)s"
)

file_handler = logging.handlers.RotatingFileHandler(
    'ployquant.log', mode="a", maxBytes=1024 * 1024 * 8, backupCount=1
)
file_handler.setFormatter(rh_formatter)
logger.addHandler(file_handler)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(rh_formatter)
logger.addHandler(stdout_handler)
""" Logger functionality for Vane to add logs to vane.log file"""

import logging
import os

FORMAT = "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"

LOG_DIRECTORY = "logs"
os.makedirs(LOG_DIRECTORY, exist_ok=True)
log_file = os.path.join(LOG_DIRECTORY, "vane.log")

logging.basicConfig(
    level=logging.INFO,
    filename=log_file,
    filemode="w",
    format=FORMAT,
)

logging = logging.getLogger("vane_logs")

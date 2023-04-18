""" Logger functionality for Vane to add logs to vane.log file"""

import logging

FORMAT = "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"

logging.basicConfig(
    level=logging.INFO,
    filename="vane.log",
    filemode="w",
    format=FORMAT,
)

logging = logging.getLogger("vane_logs")

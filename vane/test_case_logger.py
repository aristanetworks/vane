""" Logger functionality for Vane testcases to add logs to vane html report and vane_test.log"""

import logging

# pylint: disable=consider-using-with


def setup_logger(log_file):
    """Creating logger per test case basis"""

    log_file = log_file.split("/")[-1:][0][:-3] + ".log"
    # Creating a logger object for the given test case file
    logger = logging.getLogger(log_file)
    logger.setLevel(logging.INFO)
    formatter_test = logging.Formatter(
        "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"
    )

    # Test cases should not propagate to vane.logs file
    logger.propagate = False

    # Create the log file if it doesn't exist
    path = "logs/" + log_file
    open(path, "a", encoding="utf-8").close()

    # Logger functionality for Vane testcases to add logs to test case specific log file
    file_handler_test = logging.FileHandler(path, mode="w")
    file_handler_test.setFormatter(formatter_test)
    logger.addHandler(file_handler_test)

    # Logger functionality for Vane testcases to add logs to vane html report"""
    console_handler_test = logging.StreamHandler()
    console_handler_test.setFormatter(formatter_test)
    logger.addHandler(console_handler_test)

    return logger

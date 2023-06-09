import logging
import sys
from datetime import datetime
from os import path, mkdir


class __RemoveNewlineFormatter(logging.Formatter):
    def format(self, record) -> str:
        msg: str = super().format(record)
        if msg.rstrip() == '':
            return ""
        return msg.rstrip()


class __StdoutToLogger:
    pattern: str = r".+ - MyLogger - (INFO|WARNING|ERROR) -"

    def __init__(self, logger_inner) -> None:
        self.logger = logger_inner

    def write(self, message: str) -> None:
        if message.rstrip() != "":
            self.logger.info(message.rstrip())

    def flush(self) -> None:
        pass


def __create_logs_folder() -> None:
    if not path.exists("logs"):
        mkdir("logs")


# create logger
logger = logging.getLogger('LOGGER')
logger.setLevel(logging.DEBUG)

__create_logs_folder()

# create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# create file handler and set level to INFO
filename: str = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S") + '_logfile.log'

file_handler = logging.FileHandler(f'logs/{filename}')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(__RemoveNewlineFormatter(formatter._fmt))

# create console handler and set level to INFO
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(__RemoveNewlineFormatter(formatter._fmt))

# add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

sys.stdout = __StdoutToLogger(logger)


def signal_handler(sig: int, _) -> None:
    logger.warning('Signal %s received, exiting...', sig)
    exit(0)

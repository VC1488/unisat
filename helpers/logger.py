import os
import logging
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter

def setup_logger():
    log_directory = '../logs'
    os.makedirs(log_directory, exist_ok=True)

    console_formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG':    'grey',
            'INFO':     'bold_green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red',
        }
    )

    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        os.path.join(log_directory, 'recent_logs.log'),
        maxBytes=5*1024*1024,
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()
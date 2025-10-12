# import logging
# import os
# from datetime import datetime

# LOGS_DIR = "logs"
# os.makedirs(LOGS_DIR,exist_ok=True)

# LOG_FILE = os.path.join(LOGS_DIR, f"log_{datetime.now().strftime('%Y-%m-%d')}.log")

# logging.basicConfig(
#     filename=LOG_FILE,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

# def get_logger(name):
#     logger = logging.getLogger(name)
#     logger.setLevel(logging.INFO)
#     return logger


import logging
from datetime import datetime
from pathlib import Path


# Get the anime_recommender package root directory
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = PACKAGE_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / f"log_{datetime.now().strftime('%Y-%m-%d')}.log"


logging.basicConfig(
    filename=str(LOG_FILE),
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger

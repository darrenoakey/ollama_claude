import logging
from pathlib import Path

LOG_DIR = Path("output")


# ##################################################################
# setup logger
# configures logging to both console and file in output directory
def setup_logger(name: str) -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    log_file = LOG_DIR / "server.log"

    file_handler = logging.FileHandler(log_file, mode="a")
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# ##################################################################
# get logger
# retrieves or creates logger for given module name
def get_logger(name: str) -> logging.Logger:
    return setup_logger(name)

import logging
import os

_logging_configured = False


def setup_logging(force: bool = False) -> None:
    global _logging_configured

    if not force and _logging_configured:
        return

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # force configure root logger - remove any existing handlers and add ours
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # remove any existing handlers
    root_logger.setLevel(level)

    # add our handler with priority
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)

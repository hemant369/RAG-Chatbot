import logging
import os
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class ImmediateFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()


def setup_logger(name: str = "rag") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        file_handler = ImmediateFileHandler(LOG_DIR / "rag.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


def is_main_process() -> bool:
    """
    Check if this is the main process (not the reloader process).

    When FastAPI runs with reload=True, it spawns a child process for hot reload.
    This causes module-level code to run twice, creating duplicate logs.

    Returns:
        bool: True if this is the main process, False if reloader process
    """
    # Check if we're in the main process
    return os.getenv("FASTAPI_MAIN_PROCESS") == "1" or not os.getenv("RUN_MAIN")


logger = setup_logger("rag")
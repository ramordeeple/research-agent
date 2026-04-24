import logging
import sys
from typing import Final


from src.core.config import get_settings

NOISY_LOGGERS: Final[tuple[str, ...]] = ("httpx", "httpcore")

def setup_logging():
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)s: %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    for name in NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)
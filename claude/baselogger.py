import logging
from pathlib import Path

LOG_DIR = Path("./logs")
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("jordans-music")
logger.setLevel(logging.DEBUG)

_handler = logging.FileHandler(LOG_DIR / "logs.log")
_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
)
logger.addHandler(_handler)

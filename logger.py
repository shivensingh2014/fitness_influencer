"""
Centralized logging for Genfluence.
Import `log` from here in every module.
Logs go to both console (coloured) and a rotating file in output/genfluence.log.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# ── Log file lives in output/ ─────────────────────────────────────────
LOG_DIR = Path(__file__).parent / "output"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "genfluence.log"

# ── Formatter ─────────────────────────────────────────────────────────
FMT = "%(asctime)s │ %(levelname)-8s │ %(name)-24s │ %(message)s"
DATE_FMT = "%H:%M:%S"


def _build_logger() -> logging.Logger:
    logger = logging.getLogger("genfluence")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger  # already configured

    # Console handler – INFO and above, coloured level
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(FMT, datefmt=DATE_FMT))
    logger.addHandler(console)

    # File handler – DEBUG and above, rotating 2 MB × 3 backups
    file_h = RotatingFileHandler(
        LOG_FILE, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    file_h.setLevel(logging.DEBUG)
    file_h.setFormatter(logging.Formatter(FMT, datefmt=DATE_FMT))
    logger.addHandler(file_h)

    return logger


log = _build_logger()

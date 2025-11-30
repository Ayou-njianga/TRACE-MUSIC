# utils/logging_config.py
import logging
import sys
from pathlib import Path

def setup_logging(level=logging.INFO, logfile: str | None = None):
    """Configure root logger for the project."""
    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    handlers = [logging.StreamHandler(sys.stdout)]
    if logfile:
        logdir = Path(logfile).parent
        logdir.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(logfile))
    logging.basicConfig(level=level, format=fmt, handlers=handlers)
    # return a module logger factory
    def get(name=__name__):
        return logging.getLogger(name)
    return get

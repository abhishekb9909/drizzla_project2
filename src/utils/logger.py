import sys
from pathlib import Path
from loguru import logger as _logger

from src.utils.config import config

# Ensure logs directory exists
log_dir = Path(config.LOG_DIR)
log_dir.mkdir(parents=True, exist_ok=True)

# Configure loguru
_logger.remove()  # Remove default handler
_logger.add(
    sys.stderr,
    level=config.LOG_LEVEL,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
_logger.add(
    log_dir / "rag_system.log",
    level=config.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="500 MB",
    retention="10 days"
)

logger = _logger

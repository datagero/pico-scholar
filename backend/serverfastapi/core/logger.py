import logging
from core.config import settings

# Configure the logging level based on environment variables
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create a logger instance
logger = logging.getLogger(__name__)

def get_logger(name: str):
    """Return a logger instance with the given name."""
    return logging.getLogger(name)

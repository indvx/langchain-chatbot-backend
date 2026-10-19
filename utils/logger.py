import logging
import os

# Centralized application logging configuration.
# Writes structured logs simultaneously to logs/app.log and stdout.
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Check root_logger.hasHandlers() to avoid attaching multiple handlers 
# whenever Uvicorn auto-reloads during local development.
root_logger = logging.getLogger()
if not root_logger.hasHandlers():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

# Suppress verbose file polling logs from uvicorn --reload's file watcher
logging.getLogger("watchfiles").setLevel(logging.WARNING)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)

# Shared logger instance used across routers, services, and background jobs
logger = logging.getLogger("app_logger")
logger.info("Logger initialized successfully.")


import os

APP_VERSION = os.getenv("APP_VERSION", "unknown")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 10))
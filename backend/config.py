from pathlib import Path
import os


SHARED_DIR = Path(os.getenv("SHARED_DIR"))  # Path("/shared")
SHARED_DIR.mkdir(exist_ok=True)

SHARED_TMP_UPLOAD_DIR = SHARED_DIR/"tmp_upload"
SHARED_TMP_UPLOAD_DIR.mkdir(exist_ok=True)

SHARED_CELERY_WORKER_DIR = Path(os.getenv("SHARED_CELERY_DIR"))
SHARED_CELERY_WORKER_DIR.mkdir(exist_ok=True)

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_BACKEND_DB_NAME = os.getenv("CELERY_BACKEND_DB_NAME")
CELERY_BACKEND_URL = f"db+sqlite:///{SHARED_CELERY_WORKER_DIR}/{CELERY_BACKEND_DB_NAME}"

PDFALTO_API_URL = "http://pdfalto:8080/generate"

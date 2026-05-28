import sqlite3
from celery import Celery, shared_task, signals
from celery.schedules import timedelta
from sqlalchemy import event
from sqlalchemy.engine import Engine

# from celeryApp.celery_custom_utils import CustomSQLiteBackend
from config import CELERY_BACKEND_URL, CELERY_BROKER_URL

celery_app = Celery(
    "pdf_tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_BACKEND_URL,
    include=["services.tasks"],
)


# function to enable wal mode
def enable_wal_mode(dbapi_connection, *args):
    cursor = dbapi_connection.cursor()
    cursor.execute("pragma journal_mode=wal;")
    cursor.close()

# ensure wal mode setup on database connections
event.listen(Engine, "connect", enable_wal_mode)

# set the custom sqlite backend
celery_app.conf.update(
    result_backend=CELERY_BACKEND_URL,
    task_time_limit=3600,
    result_expires=3600,
    task_track_started=True,
    task_ignore_result=False,
    result_extended=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    print("setting up periodic tasks...")
    sender.add_periodic_task(
        timedelta(hours=1),
        celery_app.tasks["celery.backend_cleanup"].s(),
        name="Periodic Cleanup of Expired Results",
        queue="maintenance",
    )
    sender.add_periodic_task(
        timedelta(hours=2),
        vacuum_database.s(),
        name="Vacuum Database",
        queue="maintenance",
    )


# @signals.task_prerun.connect
# def check_db_before_task(*args, **kwargs):
#     ensure_database_exists()
#     ensure_celery_tables_exist()


@shared_task
def vacuum_database():
    db_path = CELERY_BACKEND_URL.replace("db+sqlite:///", "")  # Extract the DB path
    conn = sqlite3.connect(db_path)
    conn.execute("VACUUM;")
    conn.close()

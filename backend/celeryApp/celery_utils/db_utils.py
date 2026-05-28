# from celeryApp.celery_app import ensure_database_exists, ensure_celery_tables_exist
#
# from functools import wraps
#
#
# def ensure_db(func):
#     @wraps(func)  # this preserves the original function signature
#     async def wrapper(*args, **kwargs):
#         ensure_database_exists()
#         ensure_celery_tables_exist()
#         return await func(*args, **kwargs)
#
#     return wrapper

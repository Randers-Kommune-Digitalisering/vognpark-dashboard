from utils.database import DatabaseClient
from utils.config import (
    VOGNPARK_POSTGRES_DB_HOST, VOGNPARK_POSTGRES_DB_USER, VOGNPARK_POSTGRES_DB_PASS,
    VOGNPARK_POSTGRES_DB_DATABASE, VOGNPARK_POSTGRES_DB_PORT
)


def get_vognpark_db():
    return DatabaseClient(
        db_type='postgresql',
        database=VOGNPARK_POSTGRES_DB_DATABASE,
        username=VOGNPARK_POSTGRES_DB_USER,
        password=VOGNPARK_POSTGRES_DB_PASS,
        host=VOGNPARK_POSTGRES_DB_HOST,
        port=VOGNPARK_POSTGRES_DB_PORT
    )

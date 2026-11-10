import mysql.connector

from config import DB_CONFIG


def get_db_connection():
    connection = mysql.connector.connect(
        **DB_CONFIG,
        connection_timeout=5
    )

    return connection
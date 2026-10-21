

import os

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Create and return a MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "cpu_scheduler_db"),
        )
        return connection

    except Error as error:
        raise RuntimeError(
            f"Could not connect to MySQL: {error}"
        ) from error
    
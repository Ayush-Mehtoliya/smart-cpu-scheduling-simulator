
from database.db import get_connection


def main():
    connection = get_connection()

    try:
        if connection.is_connected():
            print("SUCCESS: Connected to cpu_scheduler_db")

            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")

            print("Tables found:")
            for row in cursor.fetchall():
                print("-", row[0])

            cursor.close()
    finally:
        connection.close()


if __name__ == "__main__":
    main()

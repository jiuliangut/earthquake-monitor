"""File that connects API to RDS."""
import os
import logging
from typing import Any
import psycopg2
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor, RealDictRow
from dotenv import load_dotenv

load_dotenv()

JOINED_TABLES = """SELECT  a.alert_type AS alert_level,
                e.earthquake_id,
                e.magnitude,
                e.cdi,
                e.felt_report_count,
                e.place,
                e.longitude,
                e.latitude,
                e.depth,
                e.detail_url,
                e.time,
                m.magnitude_type,
                n.network_name
                FROM earthquakes e
                JOIN alerts a ON e.alert_id = a.alert_id
                JOIN magnitude_types m ON e.magnitude_id = m.magnitude_id
                JOIN networks n ON e.network_id = n.network_id"""

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_connection() -> connection:
    """ Establishes a connection with database. """
    logging.info("Attempting to connect to the database")
    try:
        conn = psycopg2.connect(dbname=os.getenv("DB_NAME"),
                                user=os.getenv("DB_USER"),
                                password=os.getenv("DB_PASSWORD"),
                                host=os.getenv("DB_HOST"),
                                port=os.getenv("DB_PORT"))
        logging.info("Database connection successful.")
        return conn
    except KeyError as e:
        logging.error("%s missing from environment variables.", e)
        raise
    except psycopg2.OperationalError as e:
        logging.error("Error connecting to database: %s", e)
        raise
    except Exception as e:
        logging.error("Unexpected error while connecting to database: %s", e)
        raise


def get_cursor(connect: connection) -> cursor:
    """ Create a cursor to send and receive data. """
    logging.info("Creating database cursor")
    try:
        return connect.cursor(cursor_factory=RealDictCursor)
    except Exception as e:
        logging.error("Failed to create cursor: %s", e)
        raise


def get_earthquake_by_id(earthquake_id: int) -> dict[str, Any]:
    conn = get_connection()
    app_cursor = get_cursor(conn)

    app_cursor.execute(f"{JOINED_TABLES} WHERE earthquake_id={earthquake_id}")
    return app_cursor.fetchall()


def get_earthquakes_by_magnitude(min_magnitude: float = -1.0, max_magnitude: float = 10.0) -> list[dict]:
    """Returns all earthquakes based on the parameters."""

    conn = get_connection()
    app_cursor = get_cursor(conn)

    app_cursor.execute(
        f"{JOINED_TABLES} WHERE e.magnitude BETWEEN {min_magnitude} AND {max_magnitude}")
    return app_cursor.fetchall()


def get_earthquakes_by_date(start_date: str, end_date: str, sort: str) -> list[dict]:
    """Returns all earthquakes within a date range."""

    conn = get_connection()
    app_cursor = get_cursor(conn)

    query = f"""{JOINED_TABLES} WHERE e.time::date BETWEEN %s AND %s 
            ORDER BY time {sort}"""

    app_cursor.execute(query, (start_date, end_date))
    return app_cursor.fetchall()


def get_earthquakes_by_alert_level(color: str):
    """Returns all earthquakes with a certain alert level."""
    conn = get_connection()
    app_cursor = get_cursor(conn)

    app_cursor.execute(f"{JOINED_TABLES} WHERE a.alert_type = '{color}'")

    return app_cursor.fetchall()

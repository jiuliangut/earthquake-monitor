"""Data retrieval from rds for dashboard visualisations."""

import os
import logging
import psycopg2
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import pandas as pd

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_connection() -> connection:
    """ Establishes a connection with database. """
    load_dotenv()

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


def get_data_from_range(start_date, end_date, cursor: cursor) -> pd.DataFrame:
    """Gets all earthquake data between 2 datetimes"""

    query = """
            SELECT e.place, e.time, e.felt_report_count, e.magnitude,
                e.cdi, ROUND(e.latitude, 2) AS latitude, ROUND(e.longitude, 2) AS longitude, e.depth, a.alert_type, m.magnitude_type, 
                n.network_name
            FROM earthquakes AS e
            JOIN alerts AS a ON e.alert_id = a.alert_id
            JOIN magnitude AS m ON e.magnitude_id = m.magnitude_id
            JOIN networks AS n ON e.network_id = n.network_id
            WHERE e.time BETWEEN %s AND %s::timestamp + interval '23:59:59';
            """

    try:
        cursor.execute(query, (start_date, end_date))
        result = cursor.fetchall()
        return pd.DataFrame(result)
    except psycopg2.OperationalError as e:
        logging.error(
            "Operational error occurred connecting whilst fetching live metrics: %s", e)
        raise
    except Exception as e:
        logging.error("Error occurred whilst fetching live metrics: %s", e)
        raise

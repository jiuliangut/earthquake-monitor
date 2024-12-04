# pylint: disable=line-too-long

'''Module that inserts the transformed data into an RDS'''
import os
import logging
import psycopg2
from pandas import Timestamp
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

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


def get_foreign_key(db_cursor: psycopg2.extensions.cursor, table_name: str,
                    column_name: str, value: str) -> int:
    """ Gets foreign keys. """
    try:
        db_cursor.execute(
            f"SELECT * FROM {table_name} WHERE {column_name} = '{value}'")
        result = db_cursor.fetchone()
        if result:
            first_key = next(iter(result))
            return result[first_key]

        logging.error("Foreign key not found for %s in %s", value, table_name)
        raise ValueError('Invalid Data!')

    except psycopg2.Error as e:
        logging.error("Database error while fetching foreign key: %s", e)
        raise
    except Exception as e:
        logging.error("Unexpected error while fetching foreign key: %s", e)
        raise


def insert_into_earthquake(db_conn: connection,
                           db_cursor: cursor,
                           earthquake_data: list[dict]) -> None:
    """Inserts cleaned data into the earthquake table."""

    try:
        value_list = []

        query = """INSERT INTO earthquakes(time, tsunami, felt_report_count, magnitude,
                            cdi, latitude, longitude, detail_url, alert_id, magnitude_id, network_id, type_id) VALUES
                            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        for earthquake in earthquake_data:
            try:
                alert_id = get_foreign_key(
                    db_cursor, 'alerts', 'alert_type', earthquake['alert'])
                magnitude_id = get_foreign_key(
                    db_cursor, 'magnitude', 'magnitude_type', earthquake['magnitude_type'])
                network_id = get_foreign_key(
                    db_cursor, 'networks', 'network_name', earthquake['network'])
                type_id = get_foreign_key(
                    db_cursor, 'type', 'type_name', earthquake['type'])

                values = (
                    earthquake['at'],
                    bool(earthquake['tsunami']),
                    int(earthquake['felt']),
                    float(earthquake['magnitude']),
                    float(earthquake['cdi']),
                    float(earthquake['latitude']),
                    float(earthquake['longitude']),
                    earthquake['event_url'],
                    alert_id,
                    magnitude_id,
                    network_id,
                    type_id
                )

                value_list.append(values)

            except ValueError as e:
                logging.error("Skipping record due to ValueError: %s", e)
                continue
            except Exception as e:
                logging.error(
                    "Unexpected error while processing earthquake data: %s", e)
                continue

        if value_list:
            logging.info(
                "Inserting %s records into the earthquake table", len(value_list))
            db_cursor.executemany(query, value_list)
            db_conn.commit()
            logging.info("Data successfully inserted into the database")
        else:
            logging.warning("No valid records to insert.")

    except psycopg2.Error as e:
        logging.error("Database error while inserting earthquake data: %s", e)
        raise
    except Exception as e:
        logging.error(
            "Unexpected error while inserting earthquake data: %s", e)
        raise


def load_data(clean_data: list[dict]) -> None:
    """Calls necessary functions to upload data to rds"""
    load_dotenv()
    conn = get_connection()
    app_cursor = get_cursor(conn)
    insert_into_earthquake(conn, app_cursor, clean_data)


if __name__ == "__main__":
    test_data = [
        {
            'at': Timestamp('2024-12-02 14:44:50'),
            'event_url': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/pr2024337000.geojson',
            'felt': 0.0,
            'location': '60 km NW of Aguadilla, Puerto Rico',
            'magnitude': 3.75,
            'network': 'pr',
            'alert': 'green',
            'magnitude_type': 'md',
            'type': 'earthquake',
            'tsunami': 0,
            'cdi': 0.0,
            'longitude': -67.5815,
            'latitude': 18.7953
        },
        {
            'at': Timestamp('2024-12-01 03:22:15'),
            'event_url': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/us202433689.geojson',
            'felt': 4.0,
            'location': '10 km NE of Ridgecrest, California',
            'magnitude': 4.25,
            'network': 'ci',
            'alert': 'yellow',
            'magnitude_type': 'ml',
            'type': 'quarry',
            'tsunami': 0,
            'cdi': 3.2,
            'longitude': -117.5245,
            'latitude': 35.7038
        },
        {
            'at': Timestamp('2024-11-30 20:05:00'),
            'event_url': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/ak202433678.geojson',
            'felt': 2.0,
            'location': '50 km SW of Homer, Alaska',
            'magnitude': 4.8,
            'network': 'ak',
            'alert': 'green',
            'magnitude_type': 'mb',
            'type': 'earthquake',
            'tsunami': 1,
            'cdi': 2.7,
            'longitude': -151.7928,
            'latitude': 59.3421
        }
    ]

    load_data(test_data)

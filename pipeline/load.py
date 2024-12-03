'''Module that inserts the transformed data into an RDS'''
import os
import psycopg2
from pandas import Timestamp
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


def get_connection() -> connection:
    """ Establishes a connection with database. """
    return psycopg2.connect(f"""dbname={os.getenv("DB_NAME")}
                            user={os.getenv("DB_USER")}
                            password={os.getenv("DB_PASSWORD")}
                            host={os.getenv("DB_HOST")}
                            port={os.getenv("DB_PORT")}""")


def get_cursor(connect: connection) -> cursor:
    """ Create a cursor to send and receive data. """
    return connect.cursor(cursor_factory=RealDictCursor)


def get_foreign_key(db_cursor: psycopg2.extensions.cursor, table_name: str,
                    column_name: str, value: str) -> int:
    """ Gets foreign keys. """

    db_cursor.execute(
        f"SELECT * FROM {table_name} WHERE {column_name} = '{value}'")
    result = db_cursor.fetchone()
    if result:
        first_key = next(iter(result))
        return result[first_key]
    raise ValueError('Invalid Data!')


def insert_into_earthquake(db_conn: connection,
                           db_cursor: cursor,
                           earthquake_data: list[dict]) -> None:
    """Inserts cleaned data into the earthquake table."""
    for earthquake in earthquake_data:
        alert_id = get_foreign_key(
            db_cursor, 'alerts', 'alert_type', earthquake['alert'])
        magnitude_id = get_foreign_key(
            db_cursor, 'magnitude', 'magnitude_type', earthquake['magnitude_type'])
        network_id = get_foreign_key(
            db_cursor, 'networks', 'network_name', earthquake['network'])
        type_id = get_foreign_key(
            db_cursor, 'type', 'type_name', earthquake['type'])
        query = """
            INSERT INTO earthquakes (time, tsunami, felt_report_count, magnitude, 
                          cdi, latitude, longitude, detail_url, alert_id, magnitude_id, network_id, type_id) VALUES
                          (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
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
        db_cursor.execute(query, values)

        db_conn.commit()


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

    conn = get_connection()
    app_cursor = get_cursor(conn)
    insert_into_earthquake(conn, app_cursor, test_data)

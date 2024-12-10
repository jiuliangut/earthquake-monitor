import os
import pandas as pd
import logging
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_connection() -> connection:
    '''Function to get the connection to the database'''
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


def get_required_features(rds_connection: connection) -> pd.DataFrame:
    '''Function to extract the required features for the ML code from the RDS'''
    query = """SELECT latitude, longitude, magnitude
               FROM earthquakes"""

    earthquake_features = pd.read_sql_query(query, rds_connection)
    return earthquake_features


if __name__ == "__main__":
    db_connection = get_connection()
    print(get_required_features(db_connection))

'''
Module that creates an ML model 
The model predicts the magnitude of an earthquake at a specific location
'''
import os
import pandas as pd
import logging
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

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


def get_required_features_from_db(rds_connection: connection) -> pd.DataFrame:
    '''Function to extract the required features for the ML code from the RDS'''
    query = """SELECT latitude, longitude, magnitude
               FROM earthquakes"""

    earthquake_features = pd.read_sql_query(query, rds_connection)
    return earthquake_features


def train_model(model, features: pd.DataFrame) -> None:
    '''Function to train the ML model'''
    feature_train, _, magnitude_train, _ = train_test_split(
        features[['latitude', 'longitude']], features['magnitude'], train_size=0.7, test_size=0.3)
    model.fit(feature_train, magnitude_train)
    return


def make_prediction(latitude: float, longitude: float) -> float:
    '''Function to make a prediction on a magnitude for specific long and lat values'''
    load_dotenv()
    db_connection = get_connection()
    features = get_required_features_from_db(db_connection)
    rf_model = RandomForestRegressor()
    train_model(rf_model, features)
    prediction = rf_model.predict(pd.DataFrame(
        [{"latitude": latitude, "longitude": longitude}]))
    return prediction


if __name__ == "__main__":
    print(make_prediction(51.5, -0.12))

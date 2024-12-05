# pylint: disable=line-too-long

'''
Module that transforms the extracted data into the necessary format. 
Ready to be loaded into the database
'''
import datetime
import logging
import pandas as pd

MAX_MAGNITUDE = 12.0
MIN_MAGNITUDE = -10.0
MAX_LON = 180.0
MIN_LON = -180.0
MAX_LAT = 90.0
MIN_LAT = -90.0
MAX_CDI = 12.0
MIN_CDI = 0.0
MAX_DEPTH = 1000
MIN_DEPTH = -100

GREEN = "green"
ZERO = 0

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def is_valid_latitude(lat: float) -> bool:
    """Checks if latitude is valid"""
    if not isinstance(lat, (float, int)):
        logging.error("Invalid latitude type: %s", type(lat))
        return False
    return MIN_LAT <= lat <= MAX_LAT


def is_valid_longitude(lon: float) -> bool:
    """Checks if longitude is valid"""
    if not isinstance(lon, (float, int)):
        logging.error("Invalid longitude type: %s", type(lon))
        return False
    return MIN_LON <= lon <= MAX_LON


def is_valid_magnitude(mag: float) -> bool:
    """Checks if magnitude is valid"""
    if not isinstance(mag, (float, int)):
        logging.error("Invalid magnitude type: %s", type(mag))
        return False
    return MIN_MAGNITUDE <= mag <= MAX_MAGNITUDE


def is_valid_cdi(cdi: float) -> bool:
    """Checks if cdi is valid"""
    if not isinstance(cdi, (float, int)):
        logging.error("Invalid CDI type: %s", type(cdi))
        return False
    return MIN_CDI <= cdi <= MAX_CDI


def is_valid_depth(depth: float) -> bool:
    """Checks if depth is valid"""
    if not isinstance(depth, (float, int)):
        logging.error("Invalid latitude type: %s", type(depth))
        return False
    return MIN_DEPTH <= depth <= MAX_DEPTH


def clean_data(earthquake_data: list[dict]) -> list[dict]:
    '''
    Function to clean the data extracted from the earthquake API.
    - Converts 'felt' and 'cdi' columns to numeric values, replacing invalid or missing values with defaults.
    - Replaces missing values in the 'alert' column with 'green' as the default value.
    - Gets rid of milliseconds in timestamp.
    '''

    if not earthquake_data or not isinstance(earthquake_data, list):
        logging.error("Expected list for earthquake_data, got %s",
                      type(earthquake_data))
        raise ValueError(
            "Earthquake data list is empty or not a list. Transformation cannot proceed.")

    logging.info("Cleaning earthquake data...")
    earthquake_df = pd.DataFrame(earthquake_data)

    earthquake_df["felt"] = pd.to_numeric(
        earthquake_df["felt"], errors="coerce").fillna(ZERO)
    earthquake_df["alert"] = earthquake_df["alert"].fillna(GREEN)
    earthquake_df["cdi"] = pd.to_numeric(
        earthquake_df["cdi"], errors="coerce").fillna(MIN_CDI)

    earthquake_df = validate_data(earthquake_df)

    earthquake_df["at"] = earthquake_df['at'].apply(
        lambda x: x.replace(microsecond=ZERO))

    logging.info("Data cleaning complete.")
    return earthquake_df.to_dict(orient='records')


def validate_data(earthquake_df: pd.DataFrame) -> pd.DataFrame:
    """Ensures that long, lat, magnitude, cdi readings are within a valid range"""
    logging.info("Validating data...")

    earthquake_df["latitude_valid"] = earthquake_df["latitude"].apply(
        is_valid_latitude)
    earthquake_df["longitude_valid"] = earthquake_df["longitude"].apply(
        is_valid_longitude)
    earthquake_df["magnitude_valid"] = earthquake_df["magnitude"].apply(
        is_valid_magnitude)
    earthquake_df["cdi_valid"] = earthquake_df["cdi"].apply(is_valid_cdi)
    earthquake_df["depth_valid"] = earthquake_df["depth"].apply(is_valid_depth)

    valid_earthquake_df = earthquake_df[earthquake_df["latitude_valid"] &
                                        earthquake_df["longitude_valid"] &
                                        earthquake_df["magnitude_valid"] &
                                        earthquake_df["cdi_valid"] &
                                        earthquake_df["depth_valid"]]

    invalid_count = len(earthquake_df) - len(valid_earthquake_df)
    if invalid_count > 0:
        logging.warning(
            "Removed %s invalid earthquake records.", invalid_count)

    columns_to_exclude = ["latitude_valid",
                          "longitude_valid", "magnitude_valid", "cdi_valid", "depth_valid"]

    valid_earthquake_df = valid_earthquake_df.drop(columns=columns_to_exclude)

    logging.info("Data validation complete.")
    return valid_earthquake_df

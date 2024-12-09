"""Runs the combined functions from extract.py, transform.py and load.py"""

# pylint: disable=line-too-long

from dotenv import load_dotenv
from extract import get_data
from transform import clean_data
from load import *


def lambda_handler(event, context):
    """Runs the ETL pipeline when the lambda is invoked"""
    try:
        load_dotenv()

        extracted_earthquake_data = get_data()

        if len(extracted_earthquake_data) == 0:
            return {
                "status_code": 200,
                "body": "No new earthquake data"
            }

        cleaned_earthquake_data = clean_data(extracted_earthquake_data)

        load_data(cleaned_earthquake_data)

        for earthquake in cleaned_earthquake_data:
            earthquake['at'] = str(earthquake['at'])

        return {
            "status_code": 200,
            "body": cleaned_earthquake_data
        }

    except Exception as e:
        return {
            "status_code": 500,
            "error": f"An unexpected error occurred {e}"
        }


if __name__ == "__main__":
    lambda_handler(None, None)

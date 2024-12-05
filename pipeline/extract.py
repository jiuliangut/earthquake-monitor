# pylint: disable=line-too-long

'''Module that queries all the earthquake API and stores all of the wanted data'''

from datetime import datetime
import logging
import requests

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_data() -> list[dict]:
    '''
    Function to get the necessary data from the API. 
    Only gets data that was uploaded within the last minute as the pipeline will run every minute.
    '''
    data = []
    try:
        logging.info("Fetching earthquake data from API...")
        response = requests.get(URL)

        response.raise_for_status()
        earthquakes_data = response.json()["features"]

        if not earthquakes_data:
            logging.warning("No earthquake data found in the response.")
            return []

        current_time = datetime.now()

        for earthquake_data in earthquakes_data:
            try:
                time_uploaded_at = datetime.fromtimestamp(
                    earthquake_data["properties"]["updated"] / 1000)

                if (time_uploaded_at.hour != current_time.hour or time_uploaded_at.minute < current_time.minute - 1):
                    continue

                if earthquake_data.get("properties") and earthquake_data.get("geometry"):

                    data.append({
                        "at": datetime.fromtimestamp(earthquake_data["properties"].get("time", 0) / 1000),
                        "event_url": earthquake_data["properties"].get("detail"),
                        "felt": earthquake_data["properties"].get("felt"),
                        "location": earthquake_data["properties"].get("place"),
                        "tsunami": earthquake_data["properties"].get("tsunami"),
                        "magnitude": earthquake_data["properties"]['mag'],
                        "network": earthquake_data["properties"].get("net"),
                        "alert": earthquake_data["properties"].get("alert"),
                        "magnitude_type": earthquake_data["properties"].get("magType"),
                        "type": earthquake_data["properties"].get("type"),
                        "cdi": earthquake_data["properties"]['cdi'],
                        "longitude": earthquake_data["geometry"]['coordinates'][0],
                        "latitude": earthquake_data["geometry"]['coordinates'][1],
                        "depth": earthquake_data["geometry"]['coordinates'][-1]
                    })
            except KeyError as e:
                logging.error(
                    "KeyError while processing earthquake data: %s", e)
                continue
            except Exception as e:
                logging.error("Unexpected error: %s", e)
                raise

    except requests.exceptions.RequestException as e:
        logging.error("Error fetching data from the API: %s", e)
        raise requests.exceptions.RequestException

    logging.info("Retrieved %s earthquake records.", len(data))
    return data

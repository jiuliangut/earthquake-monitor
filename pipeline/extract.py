'''Module that queries all the earthquake API and stores all of the wanted data'''
from datetime import datetime
import requests

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"


def get_data() -> list[dict]:
    '''
    Function to get the necessary data from the API. 
    Only gets data that was uploaded within the last minute as the pipeline will run every minute
    '''
    data = []
    response = requests.get(URL)
    earthquakes_data = response.json()["features"]
    current_time = datetime.now()
    for earthquake_data in earthquakes_data:
        time_uploaded_at = datetime.fromtimestamp(
            earthquake_data["properties"]["updated"]/1000)
        if (time_uploaded_at.hour != current_time.hour or
                time_uploaded_at.minute < current_time.minute - 1):
            continue
        if earthquake_data.get("properties") and earthquake_data.get("geometry"):
            data.append({
                "at": datetime.fromtimestamp(earthquake_data["properties"]["time"]/1000),
                "event_url": earthquake_data["properties"].get("detail"),
                "felt": earthquake_data["properties"].get("felt"),
                "location": earthquake_data["properties"].get("place"),
                "tsunami": earthquake_data["properties"].get("tsunami"),
                "magnitude": earthquake_data["properties"].get("mag"),
                "network": earthquake_data["properties"].get("net"),
                "alert": earthquake_data["properties"].get("alert"),
                "magnitude_type": earthquake_data["properties"].get("magType"),
                "type": earthquake_data["properties"].get("type"),
                "cdi": earthquake_data["properties"].get("cdi"),
                "longitude": earthquake_data["geometry"].get("coordinates")[0],
                "latitude": earthquake_data["geometry"].get("coordinates")[1]
            })
    return data


if __name__ == "__main__":
    print(get_data())

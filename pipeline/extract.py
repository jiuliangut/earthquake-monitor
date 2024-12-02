'''Module that queries all the earthquake API and stores all of the wanted data'''
import requests
from datetime import datetime, timedelta
import time

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"


def get_data() -> list[dict]:
    data = []
    response = requests.get(URL)
    earthquakes_data = response.json()["features"]
    current_time = datetime.now()
    for earthquake_data in earthquakes_data:
        time_uploaded_at = datetime.fromtimestamp(
            earthquake_data["properties"]["updated"]/1000)
        if time_uploaded_at.hour != current_time.hour or time_uploaded_at.minute < current_time.minute - 1:
            continue
        if earthquake_data.get("properties"):
            data.append({
                "at": datetime.fromtimestamp(earthquake_data["properties"]["time"]/1000),
                "event_url": earthquake_data["properties"]["detail"],
                "felt": earthquake_data["properties"]["felt"],
                "location": earthquake_data["properties"]["place"],
                "magnitude": earthquake_data["properties"]["mag"],
                "network": earthquake_data["properties"]["net"],
                "alert": earthquake_data["properties"]["alert"],
                "magnitude_type": earthquake_data["properties"]["magType"],
                "type": earthquake_data["properties"]["type"],
                "cdi": earthquake_data["properties"]["cdi"],
                "longitude": earthquake_data["geometry"]["coordinates"][0],
                "latitude": earthquake_data["geometry"]["coordinates"][1]
            })
    return data


if __name__ == "__main__":
    print(get_data())

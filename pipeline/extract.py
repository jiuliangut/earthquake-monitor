'''Module that queries all the earthquake API and stores all of the wanted data'''
import requests

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"


def get_data() -> list[dict]:
    data = []
    response = requests.get(URL)
    earthquakes_data = response.json()["features"]
    for earthquake_data in earthquakes_data:
        if earthquake_data.get("properties"):
            data.append({
                "at": earthquake_data["properties"]["time"],
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

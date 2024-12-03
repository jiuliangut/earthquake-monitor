'''
Module that transforms the extracted data into the necessary format. 
Ready to be loaded into the database
'''
import datetime
import pandas as pd


def clean_data(earthquake_data: list[dict]) -> pd.DataFrame:
    '''
    Function to clean the data extracted
    Replaces any None values with actual values 
    '''
    earthquake_df = pd.DataFrame(earthquake_data)
    earthquake_df["felt"] = pd.to_numeric(
        earthquake_df["felt"], errors="coerce").fillna(0)
    earthquake_df["alert"] = earthquake_df["alert"].fillna("green")
    earthquake_df["cdi"] = pd.to_numeric(
        earthquake_df["cdi"], errors="coerce").fillna(-1)
    return earthquake_df


if __name__ == "__main__":
    test_data = [{'at': datetime.datetime(2024, 12, 2, 14, 44, 50, 830000),
                  'event_url': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/pr2024337000.geojson',
                  'felt': None,
                  'location': '60 km NW of Aguadilla, Puerto Rico',
                  'magnitude': 3.75,
                  'network': 'pr',
                  'alert': None,
                  'magnitude_type': 'md',
                  'type': 'earthquake',
                  'tsunami': 0,
                  'cdi': None,
                  'longitude': -67.5815,
                  'latitude': 18.7953}]
    print(clean_data(test_data))

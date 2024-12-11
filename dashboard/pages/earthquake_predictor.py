"""Users can enter a location and see chances of an earthquake and magnitude level"""

from datetime import datetime, timedelta
import requests
import folium.map
import streamlit as st
from dotenv import load_dotenv
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from streamlit_folium import st_folium
import folium

BUCKET_NAME = "c14-earthquake-monitor-storage"


def setup_page():

    st.set_page_config(
        page_title="Predictor - Earthquake Monitor System", page_icon="🌏",
        layout="wide", initial_sidebar_state="collapsed")

    load_dotenv()

    pdf = download_pdf_from_s3()

    if pdf:
        setup_sidebar(pdf)

    emoji_left, title, emoji_right = st.columns((1, 1.5, 1))

    with emoji_left:
        st.title("🌍🌲")

    with title:
        st.markdown("<h1 style='text-align: centre;'>Earthquake Predictor</h1>",
                    unsafe_allow_html=True)

    with emoji_right:
        st.markdown("<h1 style='text-align: right;'>🌲🌍</h1>",
                    unsafe_allow_html=True)

    setup_map()


def setup_map():
    """Interactive map with a single marker that updates on click."""

    if "predict_data" not in st.session_state:
        st.session_state.predict_data = {
            "latitude": 51.381801,
            "longitude": -0.278379,
            "api_data": None
        }

    predict_data = st.session_state.predict_data

    map = folium.Map(location=[predict_data["latitude"],
                               predict_data["longitude"]], zoom_start=5)

    folium.Marker(
        location=[predict_data["latitude"], predict_data["longitude"]],
        popup="Selected Location",
        draggable=False
    ).add_to(map)

    output = st_folium(map, width=1325, height=580, key="folium_map")

    if output and output.get("last_clicked") is not None:
        predict_data["latitude"] = output["last_clicked"]["lat"]
        predict_data["longitude"] = output["last_clicked"]["lng"]

        predict_magnitude()

        st.rerun()

    if st.session_state.predict_data['api_data'] is not None:
        st.write("Prediction Data:",
                 st.session_state.predict_data['api_data'])

    st.write(f"Latitude: {predict_data['latitude']}, Longitude: {
             predict_data['longitude']}")


def predict_magnitude():
    """Predicts the magnitude by making a GET request to the API"""

    api_url = "http://35.179.166.236:5000/earthquakes/predict"

    response = requests.get(f"{api_url}?lat={st.session_state.predict_data['latitude']}&long={
                            st.session_state.predict_data['longitude']}")

    if response.status_code == 200:
        prediction_data = response.json()[0]
        st.session_state.predict_data["api_data"] = prediction_data
        st.write("Prediction Data:", prediction_data)
    else:
        st.error(f"Error: {response.status_code} - {response.text}")


def setup_sidebar(file) -> None:
    """Sets up the Streamlit sidebar"""

    st.sidebar.download_button(
        label="Download Weekly Report",
        data=file,
        file_name="earthquake_weekly_report.pdf",
        mime="application/pdf"
    )


def get_last_weeks_monday() -> str:
    """Calculates the date for this week's Monday."""
    today = datetime.today()
    days_to_subtract = today.weekday()
    monday = today - timedelta(weeks=1, days=days_to_subtract)
    return monday.strftime("%Y-%m-%d")


@st.cache_data(ttl=60*60*24*7)
def download_pdf_from_s3():
    """Fetches a PDF file from S3 and returns the file as bytes."""
    try:
        s3 = boto3.client('s3')

        monday_date = get_last_weeks_monday()
        file_name = f"{monday_date}-data.pdf"

        response = s3.get_object(Bucket=BUCKET_NAME, Key=file_name)
        pdf_file = response['Body'].read()
        return pdf_file
    except (NoCredentialsError, PartialCredentialsError) as e:
        st.error(
            f"AWS credentials not found. Please verify the configuration. {e}")
        return None
    except Exception as e:
        st.error(f"Error retrieving the file from S3: {e}")
        return None


setup_page()

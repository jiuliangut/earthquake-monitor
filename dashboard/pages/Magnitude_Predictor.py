"""Queries the API to predict a magnitude based on lat/long"""

from datetime import datetime, timedelta
import requests
import streamlit as st
from dotenv import load_dotenv
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from streamlit_folium import st_folium
import folium
import folium.map

BUCKET_NAME = "c14-earthquake-monitor-storage"

MAIN_LOGO = "main_logo.png"
SIDE_LOGO = "side_logo.png"


def setup_page():
    """Sets up the magnitude page"""
    st.set_page_config(
        page_title="Predictor - Earthquake Monitor System", page_icon="🌏",
        layout="wide", initial_sidebar_state="collapsed"
    )

    load_dotenv()
    pdf = download_pdf_from_s3()

    st.logo(SIDE_LOGO, icon_image=MAIN_LOGO)

    if pdf:
        setup_sidebar(pdf)

    _, title, _ = st.columns((1, 1.1, 1))

    with title:
        st.markdown(
            "<h1 style='text-align: center; padding: 16px;'>Earthquake Predictor</h1>",
            unsafe_allow_html=True,
        )

    _, centre_m, _ = st.columns([1, 15, 1])

    with centre_m:

        left, right = st.columns([2, 2], gap="medium")

        with left:
            setup_map()

        with right:
            st.markdown("<div style='padding: 8px;'></div>",
                        unsafe_allow_html=True)
            present_data()


def present_data():
    """Presents the predicted magnitude data with the lat/long."""
    predict_data = st.session_state.predict_data

    if predict_data['api_data'] is not None:
        predicted_magnitude = "{:.2f}".format(predict_data['api_data'])
        latitude = "{:.2f}".format(predict_data['latitude'])
        longitude = "{:.2f}".format(predict_data['longitude'])

        tab1, tab2 = st.tabs(["Prediction", "Details"])

        with tab1:
            st.metric(label="Predicted Magnitude:", value=predicted_magnitude)

        with tab2:
            st.metric(label="Latitude:", value=latitude)
            st.metric(label="Longitude:", value=longitude)
    else:
        st.info("Click on the map to select a location and see predictions.")


def setup_map():
    """Interactive map with a single marker that updates on click."""
    if "predict_data" not in st.session_state:
        st.session_state.predict_data = {
            "latitude": 51.381801,
            "longitude": -0.278379,
            "api_data": None,
        }

    predict_data = st.session_state.predict_data

    map = folium.Map(
        location=[predict_data["latitude"], predict_data["longitude"]],
        zoom_start=5,
    )

    folium.Marker(
        location=[predict_data["latitude"], predict_data["longitude"]],
        popup="Selected Location",
        draggable=False,
    ).add_to(map)

    st.markdown("<div style='padding: 8px;'></div>", unsafe_allow_html=True)
    output = st_folium(map, width=850, height=580, key="folium_map")

    if output and output.get("last_clicked") is not None:
        predict_data["latitude"] = output["last_clicked"]["lat"]
        predict_data["longitude"] = output["last_clicked"]["lng"]

        predict_magnitude()
        st.rerun()


def predict_magnitude():
    """Predicts the magnitude by making a GET request to the API."""
    api_url = "http://35.179.166.236:5000/earthquakes/predict"
    response = requests.get(
        f"{api_url}?lat={st.session_state.predict_data['latitude']}&long={
            st.session_state.predict_data['longitude']}"
    )

    if response.status_code == 200:
        prediction_data = response.json()[0]
        st.session_state.predict_data["api_data"] = prediction_data
    else:
        st.error(f"Error: {response.status_code} - {response.text}")


def setup_sidebar(file):
    """Sets up the Streamlit sidebar."""
    st.sidebar.markdown("<div style='padding: 16px;'>", unsafe_allow_html=True)
    st.sidebar.download_button(
        label="Download Weekly Report",
        data=file,
        file_name="earthquake_weekly_report.pdf",
        mime="application/pdf",
    )
    st.sidebar.markdown("</div>", unsafe_allow_html=True)


def get_last_weeks_monday():
    """Calculates the date for this week's Monday."""
    today = datetime.today()
    days_to_subtract = today.weekday()
    monday = today - timedelta(weeks=1, days=days_to_subtract)
    return monday.strftime("%Y-%m-%d")


@st.cache_data(ttl=60 * 60 * 24 * 7)
def download_pdf_from_s3():
    """Fetches a PDF file from S3 and returns the file as bytes."""
    try:
        s3 = boto3.client("s3")

        monday_date = get_last_weeks_monday()
        file_name = f"{monday_date}-data.pdf"

        response = s3.get_object(Bucket=BUCKET_NAME, Key=file_name)
        pdf_file = response["Body"].read()
        return pdf_file
    except (NoCredentialsError, PartialCredentialsError) as e:
        st.error(
            f"AWS credentials not found. Please verify the configuration. {e}")
        return None
    except Exception as e:
        st.error(f"Error retrieving the file from S3: {e}")
        return None


setup_page()

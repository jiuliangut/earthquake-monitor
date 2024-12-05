"""Streamlit Dashboard for earthquake monitor system"""

from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import pydeck as pdk
from db_queries import *
import boto3


BUCKET_NAME = "c14-earthquake-monitor-storage"


def setup_page() -> None:
    """Sets up Streamlit page"""
    st.set_page_config(page_title="Earthquake Monitor System",
                       page_icon="🌏", layout="wide", initial_sidebar_state="collapsed")

    pdf = download_pdf_from_s3()

    setup_sidebar(pdf)

    emoji_left, title, emoji_right = st.columns((1, 1.5, 1))

    with emoji_left:
        st.title("🌍🌲")

    with title:
        st.markdown("<h1 style='text-align: centre;'>Earthquake Monitor System</h1>",
                    unsafe_allow_html=True)

    with emoji_right:
        st.markdown("<h1 style='text-align: right;'>🌍🌲</h1>",
                    unsafe_allow_html=True)

    conn = get_connection()
    cursor = get_cursor(conn)

    date_range = get_dates()

    if date_range:
        start_date, end_date = date_range
        filtered_data = get_data_from_range(start_date, end_date, cursor)

        if not filtered_data.empty:

            earthquake_df = validate_df(filtered_data)

            earthquake_map(earthquake_df)

            recent_table(earthquake_df)

            biggest_earthquake_table(earthquake_df)
        else:
            st.warning("There is no data for this time frame")


def get_dates() -> datetime.date:
    """Filters teh dataframe by date"""
    selected_date_range = st.date_input(
        "Select Date Range", value=(datetime(2024, 12, 1), datetime.today()))

    if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
        start_date, end_date = selected_date_range

        if start_date and end_date:
            return start_date, end_date
    else:
        st.warning("Please select both a start and an end date.")


def validate_df(earthquake_df: pd.DataFrame) -> pd.DataFrame:
    """Converts decimal data type to float"""
    earthquake_df['latitude'] = earthquake_df['latitude'].astype(float)
    earthquake_df['longitude'] = earthquake_df['longitude'].astype(
        float)
    earthquake_df['magnitude'] = earthquake_df['magnitude'].astype(
        float)
    earthquake_df['depth'] = earthquake_df['depth'].astype(float)
    earthquake_df['cdi'] = earthquake_df['cdi'].astype(float)

    return earthquake_df


def earthquake_map(earthquake_df: pd.DataFrame):
    """Displays earthquake data on a world map"""
    map_df = earthquake_df.copy()

    map_df['time'] = map_df['time'].dt.strftime(
        '%Y-%m-%d %H:%M:%S')

    map_df['size'] = map_df['magnitude'].apply(lambda x: x * 2000)

    color_map = {
        "green": [0, 255, 0],
        "yellow": [255, 255, 0],
        "red": [255, 0, 0],
    }

    map_df['colour'] = map_df['alert_type'].map(
        color_map)

    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        id="earthquake-points",
        get_position=["longitude", "latitude"],
        pickable=True,
        auto_highlight=True,
        get_radius="size",
        radius_min_pixels=6,
        radius_max_pixels=1000,
        get_color="colour"
    )

    tooltip = {
        "html": """
        <div>
            <span style="color: orange; font-weight: bold;">Location:</span>
            <span style="color: white;">{place}</span><br>
            <span style="color: orange; font-weight: bold;">Time:</span>
            <span style="color: white;">{time}</span><br>
            <span style="color: orange; font-weight: bold;">Magnitude:</span>
            <span style="color: white;">{magnitude}</span><br>
            <span style="color: orange; font-weight: bold;">Depth:</span>
            <span style="color: white;">{depth}</span>
        </div>
    """,
        "style": {
            "backgroundColor": "black"
        },
    }

    chart = pdk.Deck(point_layer, tooltip=tooltip)

    selected_data = st.pydeck_chart(
        chart, on_select="rerun", selection_mode="multi-object")

    st.subheader("Details of Selected Earthquakes")

    selected_objects = selected_data.selection.get(
        "objects", {}).get("earthquake-points", [])

    if selected_objects:
        selected_df = pd.DataFrame(selected_objects)

        selected_df = selected_df.drop(columns=['size', 'colour'])

        st.dataframe(selected_df, hide_index=True)
    else:
        st.info("No earthquakes selected.")


def recent_table(earthquake_df: pd.DataFrame):
    """Gets the 5 most recent earthquakes"""
    recent_df = earthquake_df.sort_values(by="time", ascending=False).head(5)
    st.subheader("5 Most Recent Earthquakes")
    st.dataframe(recent_df, hide_index=True, use_container_width=True)


def biggest_earthquake_table(earthquake_df: pd.DataFrame):
    """Gets the biggest earthquake of the week"""
    one_week_ago = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=7)
    last_week_earthquakes = earthquake_df[earthquake_df["time"]
                                          >= one_week_ago]

    if last_week_earthquakes.empty:
        st.subheader("Biggest Earthquake of the Week")
        st.write("No earthquakes recorded in the last 7 days.")
    else:
        biggest_earthquake = last_week_earthquakes.loc[
            last_week_earthquakes["magnitude"].idxmax()
        ]
        st.subheader("Biggest Earthquake of the Week")
        st.dataframe(biggest_earthquake.to_frame().T,
                     hide_index=True, use_container_width=True)


def convert_df(df: pd.DataFrame):
    return df.to_csv().encode("utf-8")


def setup_sidebar(file) -> None:
    """Sets up the Streamlit sidebar"""

    st.sidebar.download_button(
        label="Download Weekly report as PDF",
        data=file,
        file_name="earthquake_weekly_report.pdf",
        mime="application/pdf"
    )


def get_this_weeks_monday() -> str:
    """Calculates the date for this week's Monday."""
    today = datetime.today()
    days_to_subtract = today.weekday()
    monday = today - timedelta(days=days_to_subtract)
    return monday.strftime("%Y-%m-%d")


@st.cache_data(ttl=60*60*24*7)
def download_pdf_from_s3():
    """Fetches a PDF file from S3 and returns the file as bytes."""
    try:
        s3 = boto3.client('s3')

        monday_date = get_this_weeks_monday()
        file_name = f"{monday_date}-data.pdf"

        response = s3.get_object(Bucket=BUCKET_NAME, Key=file_name)
        pdf_file = response['Body'].read()
        return pdf_file
    except Exception as e:
        st.error(f"Error retrieving the file from S3: {e}")
        return None


setup_page()

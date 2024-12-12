"""Streamlit Dashboard for earthquake monitor system"""

from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import pydeck as pdk
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
from db_queries import get_connection, get_cursor, get_data_from_range

BUCKET_NAME = "c14-earthquake-monitor-storage"

MAIN_LOGO = "main_logo.png"
SIDE_LOGO = "side_logo.png"


def setup_page() -> None:
    """Sets up Streamlit page"""
    st.set_page_config(
        page_title="Earthquake Monitor System",
        page_icon="🌏",
        layout="wide",
        initial_sidebar_state="auto",
    )

    load_dotenv()

    st.logo(SIDE_LOGO, icon_image=MAIN_LOGO)

    pdf = download_pdf_from_s3()

    if pdf:
        setup_sidebar(pdf)

    _, title, _ = st.columns((1, 1.5, 1), gap="medium")

    with title:
        st.markdown(
            "<h1 style='text-align: center; padding: 8px;'>Earthquake Monitor System</h1>",
            unsafe_allow_html=True,
        )

    conn = get_connection()
    cursor_ = get_cursor(conn)

    _, main_centre, _ = st.columns([1, 15, 1])

    with main_centre:

        left, right = st.columns(2, gap="medium")

        with left:
            date_range = get_dates()

        with right:
            min_magnitude = st.slider("Minimum magnitude", 0.0, 12.0, step=0.1)

        if date_range:
            start_date, end_date = date_range
            filtered_data = get_data_from_range(start_date, end_date, cursor_)

            if not filtered_data.empty:

                earthquake_df = validate_df(filtered_data)

                earthquake_df = filtered_data[filtered_data['magnitude']
                                              > min_magnitude]

                earthquake_map(earthquake_df)

                recent_table(earthquake_df)

                biggest_earthquake_table(earthquake_df)
            else:
                st.warning("There is no data for this time frame")


def get_dates() -> datetime.date:
    """Filters the dataframe by date"""

    selected_date_range = st.date_input(
        "Select Date Range",
        value=(datetime.today() - timedelta(weeks=1), datetime.today()),
    )

    if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
        start_date, end_date = selected_date_range

        if start_date and end_date:
            return start_date, end_date
    else:
        st.warning("Please select both a start and an end date.")


def validate_df(earthquake_df: pd.DataFrame) -> pd.DataFrame:
    """Converts decimal data type to float"""
    earthquake_df['latitude'] = earthquake_df['latitude'].astype(float)
    earthquake_df['longitude'] = earthquake_df['longitude'].astype(float)
    earthquake_df['magnitude'] = earthquake_df['magnitude'].astype(float)
    earthquake_df['depth'] = earthquake_df['depth'].astype(float)
    earthquake_df['cdi'] = earthquake_df['cdi'].astype(float)

    return earthquake_df


def earthquake_map(earthquake_df: pd.DataFrame) -> None:
    """Displays earthquake data on a world map"""
    map_df = prepare_map_data(earthquake_df)
    point_layer = create_point_layer(map_df)
    tooltip = create_tooltip()

    st.markdown("<div style='padding: 16px;'>", unsafe_allow_html=True)
    chart = pdk.Deck(point_layer, tooltip=tooltip)
    map_data = st.pydeck_chart(
        chart, on_select="rerun", selection_mode="multi-object"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    display_selected_earthquake_details(map_data)


def prepare_map_data(earthquake_df: pd.DataFrame) -> pd.DataFrame:
    """Prepares data for displaying on the map"""
    map_df = earthquake_df.copy()
    map_df['time'] = map_df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    map_df['size'] = map_df['magnitude'].apply(lambda x: x * 1500)
    map_df['colour'] = map_df['alert_type'].map(get_color_map())
    return map_df


def get_color_map() -> dict:
    """Returns the mapping of alert types to RGB color values"""
    return {
        "green": [102, 187, 106],
        "yellow": [255, 255, 0],
        "orange": [255, 140, 0],
        "red": [255, 0, 0],
    }


def create_point_layer(map_df: pd.DataFrame) -> pdk.Layer:
    """Creates the Pydeck layer for earthquake points"""
    return pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        id="earthquake-points",
        get_position=["longitude", "latitude"],
        pickable=True,
        auto_highlight=True,
        get_radius="size",
        radius_min_pixels=5,
        radius_max_pixels=1000,
        get_color="colour",
    )


def create_tooltip() -> dict:
    """Creates the tooltip for map visualization"""
    return {
        "html": """
        <div style='padding: 8px;'>
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
        "style": {"backgroundColor": "black"},
    }


def display_selected_earthquake_details(map_data) -> None:
    """Displays the details of selected earthquakes"""
    st.subheader("Details of Selected Earthquakes")
    selected_objects = map_data.selection.get(
        "objects", {}).get("earthquake-points", [])

    if selected_objects:
        selected_df = pd.DataFrame(selected_objects)
        selected_df = selected_df.drop(
            columns=['size', 'colour'], errors='ignore')
        selected_df.columns = selected_df.columns.str.replace(
            '_', ' ', regex=False).str.title()
        st.dataframe(selected_df, hide_index=True, use_container_width=True)
    else:
        st.info("No earthquakes selected.")


def recent_table(earthquake_df: pd.DataFrame) -> None:
    """Gets the 5 most recent earthquakes"""
    st.markdown("<div style='padding: 16px;'>", unsafe_allow_html=True)
    recent_df = earthquake_df.sort_values(by="time", ascending=False).head(5)
    recent_df = recent_df.drop(
        columns=['size', 'colour'], errors='ignore')
    recent_df.columns = recent_df.columns.str.replace(
        '_', ' ', regex=False).str.title()
    st.subheader("Five Most Recent Earthquakes")
    st.dataframe(recent_df, hide_index=True, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def biggest_earthquake_table(earthquake_df: pd.DataFrame) -> None:
    """Gets the biggest earthquake of the week"""
    one_week_ago = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=7)
    last_week_earthquakes = earthquake_df[earthquake_df["time"]
                                          >= one_week_ago]

    st.subheader("Biggest Earthquake of the Week 🥇")

    if last_week_earthquakes.empty:
        st.write("No earthquakes recorded in the last 7 days.")
    else:
        biggest_earthquake = last_week_earthquakes.loc[
            last_week_earthquakes["magnitude"].idxmax()
        ]

        biggest_earthquake = biggest_earthquake.to_frame().T
        biggest_earthquake.columns = biggest_earthquake.columns.str.replace(
            '_', ' ', regex=False).str.title()

        st.dataframe(biggest_earthquake, hide_index=True,
                     use_container_width=True)


def setup_sidebar(file) -> None:
    """Sets up the Streamlit sidebar"""
    st.sidebar.markdown("<div style='padding: 16px;'>", unsafe_allow_html=True)
    st.sidebar.download_button(
        label="Download Weekly Report",
        data=file,
        file_name="earthquake_weekly_report.pdf",
        mime="application/pdf",
    )
    st.sidebar.markdown("</div>", unsafe_allow_html=True)


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
        st.error(f"Error fetching file from S3: {str(e)}")
        return None


setup_page()

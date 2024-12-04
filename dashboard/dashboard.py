"""Streamlit Dashboard for earthquake monitor system"""

from datetime import datetime as dt
import pandas as pd
import streamlit as st
import altair as alt
import plotly as px
from db_queries import *


COLOUR_PALETTE = []


def setup_page() -> None:
    """Sets up Streamlit page"""
    st.set_page_config(page_title="Earthquake Monitor System",
                       page_icon="🌏", layout="wide", initial_sidebar_state="collapsed")

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

            st.dataframe(filtered_data)

            earthquake_map(filtered_data)

            recent_table(filtered_data)

            biggest_earthquake_table(filtered_data)
        else:
            st.warning("There is no data for this time frame")


def get_dates() -> dt.date:
    """Filters teh dataframe by date"""
    selected_date_range = st.date_input(
        "Select Date Range", value=(dt(2024, 12, 1), dt.today()))

    if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
        start_date, end_date = selected_date_range

        if start_date and end_date:
            return start_date, end_date
    else:
        st.warning("Please select both a start and an end date.")


def earthquake_map(earthquake_df: pd.DataFrame):
    """Displays earthquake data on a world map"""
    ...


def recent_table(earthquake_df: pd.DataFrame):
    """Gets the 5 most recent earthquakes"""
    recent_df = earthquake_df.sort_values(by="time", ascending=False).head(5)
    st.subheader("5 Most Recent Earthquakes")
    st.dataframe(recent_df)


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
        st.table(biggest_earthquake.to_frame().T)


setup_page()


# Add location

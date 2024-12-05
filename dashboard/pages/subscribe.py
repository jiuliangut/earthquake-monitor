import re
from datetime import datetime, timedelta
import streamlit as st
import boto3

BUCKET_NAME = "c14-earthquake-monitor-storage"


def setup_page():
    """Sets up subscribe page"""
    st.set_page_config(page_title="Subscribe - Earthquake Monitor System",
                       page_icon="🌏", layout="wide", initial_sidebar_state="collapsed")

    emoji_left, title, emoji_right = st.columns((1, 2, 1))

    pdf = download_pdf_from_s3()

    setup_sidebar(pdf)

    test = [1, 2, 3, 4, 5]

    with emoji_left:
        st.title("🌍🌲")

    with title:
        st.markdown("<h1 style='text-align: centre;'>Subscribe for Earthquake Alerts</h1>",
                    unsafe_allow_html=True)

    with emoji_right:
        st.markdown("<h1 style='text-align: right;'>🌍🌲</h1>",
                    unsafe_allow_html=True)

    left, middle, right = st.columns((1, 3, 1))

    with left:
        st.write("")

    with middle:
        contact_preference = st.radio(
            "How would you like to be contacted?",
            options=["Email", "Phone", "Both"]
        )
        with st.form(key="subscribe_form", clear_on_submit=True):
            st.write("Subscription Form")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")

            email = None
            phone = None

            if contact_preference == "Email" or contact_preference == "Both":
                email = st.text_input("Email", placeholder="example@gmail.com")

            if contact_preference == "Phone" or contact_preference == "Both":
                phone = st.text_input(
                    "Phone Number", placeholder="07123456789")

            regions = st.multiselect(
                "Regions", options=test, placeholder="Choose a region")

            option_map = {
                0: "All Earthquakes",
                4: "Noticeable Earthquakes (4.0+)",
                7: "Strong Earthquakes (7.0+)"
            }

            min_magnitude = st.pills("Minimum magnitude", options=option_map.keys(
            ), format_func=lambda option: option_map[option])

            subscribe_button = st.form_submit_button("Subscribe")

            if subscribe_button:

                if not validate_name(first_name, last_name):
                    st.warning("Please provide a valid first and last name.")
                elif email and not validate_email(email):
                    st.warning("Please provide a valid email address.")
                elif phone and not validate_phone_number(phone):
                    st.warning(
                        "Please provide a valid number, must start with 07 and be 10 or 11 digits in total.")
                elif not regions:
                    st.warning("Please select at least one region.")
                else:
                    st.session_state.form_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "regions": regions,
                        "min_magnitude": min_magnitude
                    }
                    # Check if user already exists, if they do, then give them a new topic subscription
                    # If they do not exist, then add them to user table and give them the topic (Might have to mess with SNS here??)
                    st.success("Successfully subscribed!")

    with right:
        st.write("")


def validate_name(first_name: str, last_name: str) -> bool:
    """Validates the name against a regEx"""

    name_pattern = r"^[A-Za-z][a-z]+$"

    return bool(re.match(name_pattern, first_name)) and bool(re.match(name_pattern, last_name))


def validate_email(email: str) -> bool:
    """Validates the email against a regEx"""

    email_pattern = r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"

    return bool(re.match(email_pattern, email))


def validate_phone_number(phone: str) -> bool:
    """Validates the phone number against a regEx"""

    phone_pattern = r"^07\d{8,9}$"

    return bool(re.match(phone_pattern, phone))


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

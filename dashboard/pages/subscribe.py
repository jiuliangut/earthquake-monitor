"""Subscription page where users can subscribe to SNS topics for earthquake alerts"""

# pylint: disable=line-too-long

import re
from datetime import datetime, timedelta
import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
from db_queries import get_connection, get_cursor, get_regions, get_topic_arns

BUCKET_NAME = "c14-earthquake-monitor-storage"


def setup_page():
    """Sets up the subscribe page."""
    st.set_page_config(
        page_title="Subscribe - Earthquake Monitor System", page_icon="🌏",
        layout="wide", initial_sidebar_state="collapsed")

    load_dotenv()

    conn = get_connection()
    cursor_ = get_cursor(conn)
    sns_client = boto3.client('sns', region_name="eu-west-2")

    regions = get_regions(cursor_)

    pdf = download_pdf_from_s3()

    if pdf:
        setup_sidebar(pdf)

    setup_header()
    setup_subscription_form(cursor_, sns_client, regions)


def setup_header():
    """Sets up the header of the page."""
    emoji_left, title, emoji_right = st.columns((1, 2, 1))

    with emoji_left:
        st.title("🌍🌲")

    with title:
        st.markdown("<h1 style='text-align: centre;'>Subscribe for Earthquake Alerts</h1>",
                    unsafe_allow_html=True)

    with emoji_right:
        st.markdown("<h1 style='text-align: right;'>🌲🌍</h1>",
                    unsafe_allow_html=True)


def setup_subscription_form(cursor_, sns_client, regions):
    """Sets up the subscription form."""
    left, middle, right = st.columns((1, 3, 1))

    with left:
        st.write("")

    with middle:
        reset_form_data()

        contact_preference = st.radio(
            "How would you like to be contacted?",
            options=["Email", "Phone", "Both"]
        )

        form_data = st.session_state.form_data

        email, phone = None, None

        with st.form(key="subscribe_form", clear_on_submit=False):
            st.write("Subscription Form 📝")

            if contact_preference in ["Email", "Both"]:
                email = st.text_input(
                    "Email", placeholder="example@gmail.com",
                    value=form_data["email"])

            if contact_preference in ["Phone", "Both"]:
                phone = st.text_input(
                    "Phone Number", placeholder="07123456789",
                    value=form_data["phone"])

            selected_regions = st.multiselect(
                "Regions", options=regions, placeholder="Choose a region",
                default=form_data["regions"])

            min_magnitude = select_min_magnitude()

            if st.form_submit_button("Subscribe"):
                handle_subscription(cursor_, sns_client, contact_preference,
                                    email, phone, selected_regions, min_magnitude)

    with right:
        st.write("")


def select_min_magnitude():
    """Renders and handles the selection of minimum magnitude."""
    option_map = {
        0: "All Earthquakes",
        4: "Noticeable Earthquakes (4.0+)",
        7: "Strong Earthquakes (7.0+)",
    }
    return st.pills(
        "Minimum magnitude",
        options=option_map.keys(),
        format_func=lambda option: option_map[option],
        key="min_magnitude",
    )


def handle_subscription(cursor_, sns_client, contact_preference, email, phone, regions, min_magnitude):
    """Validates and processes the subscription."""
    if contact_preference in ["Email", "Both"] and not validate_email(email):
        st.warning("Please provide a valid email address.")
    elif contact_preference in ["Phone", "Both"] and not validate_phone_number(phone):
        st.warning(
            "Please provide a valid phone number (start with 07, 10-11 digits).")
    elif not regions:
        st.warning("Please select at least one region.")
    else:
        st.session_state.form_data.update({
            "preference": contact_preference,
            "email": email,
            "phone": phone,
            "regions": regions,
            "min_magnitude": min_magnitude,
        })

        add_subscription(cursor_, sns_client)
        st.success("Successfully subscribed!")
        reset_form_data()


def reset_form_data():
    """Resets the form data in session state."""
    st.session_state.form_data = {
        "preference": "",
        "email": "",
        "phone": "",
        "regions": [],
        "min_magnitude": None,
    }


def validate_email(email: str) -> bool:
    """Validates the email against a regEx"""

    if email is None:
        return False

    email_pattern = r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"

    return bool(re.match(email_pattern, email))


def validate_phone_number(phone: str) -> bool:
    """Validates the phone number against a regEx"""

    if phone is None:
        return False

    phone_pattern = r"^07\d{8,9}$"

    return bool(re.match(phone_pattern, phone))


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


def add_subscription(cursor, sns: boto3.client):
    """Subscribes the user to an SNS topic"""

    contact_preference = st.session_state.form_data["preference"]
    email = st.session_state.form_data["email"]
    phone = st.session_state.form_data["phone"]
    regions = st.session_state.form_data["regions"]
    min_magnitude = st.session_state.form_data["min_magnitude"]

    regions = [region.replace("&", "").replace(
        "(", "").replace(")", "").replace(",", "").replace(" ", "_") for region in regions]

    topic_names = [f"{region}_{min_magnitude}" for region in regions]

    topic_arns = get_topic_arns(topic_names, cursor)

    for topic_arn in topic_arns:

        if contact_preference in ["Email", "Both"]:
            sns.subscribe(
                TopicArn=topic_arn,
                Protocol='email',
                Endpoint=email
            )

        if contact_preference in ["Phone", "Both"]:
            sns.subscribe(
                TopicArn=topic_arn,
                Protocol='sms',
                Endpoint=phone
            )


setup_page()

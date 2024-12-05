import re
import streamlit as st


def setup_page():
    """Sets up subscribe page"""
    st.set_page_config(page_title="Subscribe - Earthquake Monitor System",
                       page_icon="🌏", layout="wide", initial_sidebar_state="collapsed")

    emoji_left, title, emoji_right = st.columns((1, 2, 1))

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
        with st.form(key="subscribe_form", clear_on_submit=True):
            st.write("Subscription Form")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email", placeholder="example@gmail.com")
            regions = st.multiselect(
                "Regions", options=test, placeholder="Choose a region")
            min_magnitude = st.slider("Minimum magnitude", 0.0, 12.0, step=0.1)
            subscribe_button = st.form_submit_button("Subscribe")

            if subscribe_button:

                if not validate_name(first_name, last_name):
                    st.warning("Please provide a valid first and last name.")
                elif not validate_email(email):
                    st.warning("Please provide a valid email address.")
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


setup_page()

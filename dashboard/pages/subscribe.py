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
            phone_number = st.text_input(
                "Phone number", placeholder="07123456789")
            regions = st.multiselect(
                "Regions", options=test, placeholder="Choose a region")
            min_magnitude = st.slider("Minimum magnitude", 0.0, 12.0, step=0.1)
            subscribe_button = st.form_submit_button("Subscribe")

            if subscribe_button:
                st.session_state.form_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone_number": phone_number,
                    "regions": regions,
                    "min_magnitude": min_magnitude
                }
                if validate_name(first_name, last_name) and validate_email(email) and validate_phone(phone_number):
                    # Check if user already exists, if they do, then give them a new topic subscription
                    # If they do not exist, then add them to user table and give them the topic (Might have to mess with SNS here??)
                    st.success("Successfully subscribed!")

    with right:
        st.write("")


def validate_name(first_name: str, last_name: str) -> bool:
    if first_name and last_name:
        return True

    st.warning("Please fill in your first and last name")
    return False


def validate_email(email: str) -> bool:
    if email:
        return True

    st.warning("Please fill in your email")
    return False


def validate_phone(phone_number: str) -> bool:
    if phone_number:
        return True

    st.warning("Please fill in your phone number")
    return False


setup_page()

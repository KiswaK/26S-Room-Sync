from email.utils import parsedate_to_datetime
import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Initialize sidebar
SideBarLinks()

st.title("View and Send Inquiries")

# Initialize session state for modal
if "show_success_modal" not in st.session_state:
    st.session_state.show_success_modal = False
if "reset_form" not in st.session_state:
    st.session_state.reset_form = False
if "form_key_counter" not in st.session_state:
    st.session_state.form_key_counter = 0

# Define the success dialog function
@st.dialog("Success")
def show_success_dialog():
    st.markdown(f"### Inquiry sent successfully!")
    
    # Create two buttons side by side
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Return Home", use_container_width=True):
            st.session_state.show_success_modal = False
            st.switch_page("pages/40_Renter_Home.py")
    
    with col2:
        if st.button("Stay Here", use_container_width=True):
            st.session_state.show_success_modal = False
            st.session_state.reset_form = True
            st.rerun()

# Handle form reset
if st.session_state.reset_form:
    st.session_state.form_key_counter += 1
    st.session_state.reset_form = False

# API endpoint
INQUIRIES_URL = f"http://web-api:4000/samuel/renters/{st.session_state['renter_id']}/inquiries"

# get the existing inquiries
try:
    response = requests.get(INQUIRIES_URL)
    if response.status_code == 200:
        inquiries = response.json()
    else:
        st.error(f"Failed to retrieve existing inquiries: {response.json().get('error', 'Unknown error')}")
        existing_prefs = {}
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running")
    inquiries = {}

# standardize the inquires for tablee
standardized_inquires = []
for inquiry in inquiries:
    standardized_inquires.append({
        "Listing Title": inquiry["listingTitle"],
        "Sent At": parsedate_to_datetime(inquiry["sentAt"]).strftime("%Y-%m-%d %H:%M:%S"),
        "Message": inquiry["message"],
        "Read?": "Yes" if inquiry["isRead"] else "No",
        "Response": inquiry["response"] if inquiry["response"] else "[None]"
    })

# table of inquiries
st.header("Your Inquiries")
st.table(standardized_inquires)

# Show success modal if preferences were successfully set
if st.session_state.show_success_modal:
    show_success_dialog()

# Add a button to return to Home
if st.button("Return Home"):
    st.switch_page("pages/40_Renter_Home.py")

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
LISTINGS_URL = f"http://web-api:4000/samuel/renters/{st.session_state['renter_id']}/listings"

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
    inquiries = []
    
# get the matching listings
# by prefs and deal breakers
try:
    response = requests.get(LISTINGS_URL)
    if response.status_code == 200:
        listings = response.json()
    else:
        st.error(f"Failed to retrieve matching listings: {response.json().get('error', 'Unknown error')}")
        listings = {}
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running")
    listings = []
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

## send inquiry
st.header("Send an Inquiry")
with st.form(key=f"inquiry_form_{st.session_state.form_key_counter}"):
    listing_chosen = st.selectbox("Select Listing", options=listings, format_func=lambda x: x['title'])
    message = st.text_area("Your Message")
    submitted = st.form_submit_button(label="Send Inquiry")

if submitted:
    try:
        response = requests.post(INQUIRIES_URL, json={
            'listingID': listing_chosen['listingID'],
            'message': message
        })
        if response.status_code == 201:
            st.session_state.show_success_modal = True
            st.rerun()
        else:
            st.error(f"Failed to send inquiry: {response.json().get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the API: {str(e)}")
        st.info("Please ensure the API server is running")

# table of inquiries
st.header("Previous Inquiries")
st.table(standardized_inquires)

# Show success modal if preferences were successfully set
if st.session_state.show_success_modal:
    show_success_dialog()

# Add a button to return to Home
if st.button("Return Home"):
    st.switch_page("pages/40_Renter_Home.py")

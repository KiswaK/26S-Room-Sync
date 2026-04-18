import logging
logger = logging.getLogger(__name__)
import requests

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

RENTER_URL = f'http://web-api:4000/samuel/renters/{st.session_state["renter_id"]}'

try:
    response = requests.get(RENTER_URL)
    if response.status_code == 200:
        renter_data = response.json()
        st.session_state['first_name'] = renter_data['firstName']
        st.session_state['school_name'] = renter_data['schoolName']
    else:
        st.error(f"Failed to retrieve renter information: {response.json().get('error', 'Unknown error')}")
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running")

st.title(f"Welcome Renter, {st.session_state['first_name']}.")
st.write('### What would you like to do today?')

if st.button('Set Apartment Search Criteria',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/41_Preferences.py')

if st.button('View/Send Inquiries',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/42_Inquiries.py')

if st.button('Listings Classmates Have Inquired About',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/43_Classmate_Listings.py')

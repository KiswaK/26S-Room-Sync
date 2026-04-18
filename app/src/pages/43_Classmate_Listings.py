import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

# Initialize sidebar
SideBarLinks()

st.title("Classmate Listings")

st.header(f"Listings Your Classmates at {st.session_state['school_name']} Have Inquired About")

CLASSMATE_LISTINGS_URL = f"http://web-api:4000/samuel/renters/{st.session_state['renter_id']}/classmate-listings"

try:
    response = requests.get(CLASSMATE_LISTINGS_URL)
    if response.status_code == 200:
        classmate_listings = response.json()
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running")

table_data = []

# standardize data for table
for listing in classmate_listings:
    table_data.append({
        'Listing Title': listing['title'],
        'Availibility': listing['status'],
        'Availible From': listing['availableDate'],
        'Broker Fee': listing['brokerFee'],
    })


st.table(table_data)
import logging
import streamlit as st
import requests
from modules.nav import SideBarLinks

logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')
SideBarLinks()

if 'authenticated' not in st.session_state:
    st.switch_page('Home.py')

landlord_id = st.session_state['landlord_id']
API = "http://web-api:4000"

st.title("Performance Dashboard")

try:
    r = requests.get(f"{API}/eliot/landlord/{landlord_id}/listings/performance")
    
    if r.status_code == 200:
        data = r.json()
        st.write(data)
        
        if not data:
            st.info("No performance data found.")
        else:
            # Summary metrics across all listings
            total_views    = sum(row['viewCount'] for row in data)
            total_inquiries = sum(row['totalInquiries'] for row in data)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Listings", len(data))
            col2.metric("Total Views",    total_views)
            col3.metric("Total Inquiries", total_inquiries)
            
            st.subheader("Per Listing Breakdown")
            st.dataframe(data, use_container_width=True)
    else:
        st.error(f"Error fetching performance data: {r.text}")

except Exception as e:
    st.error(f"Error connecting to API: {e}")
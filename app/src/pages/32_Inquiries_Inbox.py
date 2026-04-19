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

st.title("Inquiries Inbox")

try:
    r = requests.get(f"{API}/marcus/landlord/{landlord_id}/listings")

    st.write(f"Status code: {r.status_code}")
    st.write(f"Response: {r.text}")

    listings = r.json()

    if not listings:
        st.info("No listings found.")
    else:
        listing_options = {f"Unit {l['unitNumber']}": l['listingID'] for l in listings}
        selected = st.selectbox("Select a Listing", list(listing_options.keys()))
        listing_id = listing_options[selected]

        r2 = requests.get(f"{API}/marcus/landlord/{landlord_id}/listings/{listing_id}/inquiries")
        inquiries = r2.json()

        if not inquiries:
            st.info("No inquiries for this listing.")
        else:
            for inq in inquiries:
                with st.expander(f"{'✅' if inq['isRead'] else '🔵'} {inq['sentAt']}"):
                    st.write(f"**Message:** {inq['message']}")
                    
                    if not inq['isRead']:
                        if st.button("Mark as Read", key=f"read_{inq['inquiryID']}"):
                            r3 = requests.put(
                                f"{API}/marcus/landlord/{landlord_id}/inquiries/{inq['inquiryID']}/read"
                            )
                            if r3.status_code == 200:
                                st.success("Marked as read!")
                            else:
                                st.error(f"Error: {r3.text}")

except Exception as e:
    st.error(f"Error connecting to API: {e}")
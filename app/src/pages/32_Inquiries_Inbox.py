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
    r = requests.get(f"{API}/eliot/landlord/{landlord_id}/listings")

    listings = r.json()

    if not listings:
        st.info("No listings found.")
    else:
        listing_options = {f"Unit {l['unitNumber']}": l['listingID'] for l in listings}
        selected = st.selectbox("Select a Listing", list(listing_options.keys()))
        listing_id = listing_options[selected]

        r2 = requests.get(f"{API}/eliot/landlord/{landlord_id}/listings/{listing_id}/inquiries")
        inquiries = r2.json()

        if not inquiries:
            st.info("No inquiries for this listing.")
        else:
            for inq in inquiries:
                status_icon = '✅' if inq['isRead'] else '🔵'
                with st.expander(f"{status_icon} {inq['sentAt']}"):
                    st.write(f"**Message:** {inq['message']}")

                    if inq.get('response'):
                        st.write(f"**Your Response:** {inq['response']}")
                    else:
                        response_text = st.text_area(
                            "Write your response",
                            key=f"resp_{inq['inquiryID']}",
                            placeholder="Type your reply here..."
                        )
                        if st.button("Send Response", key=f"send_{inq['inquiryID']}"):
                            if response_text.strip():
                                r3 = requests.put(
                                    f"{API}/eliot/landlord/{landlord_id}/inquiries/{inq['inquiryID']}/respond",
                                    json={"response": response_text.strip()}
                                )
                                if r3.status_code == 200:
                                    st.success("Response sent!")
                                    st.rerun()
                                else:
                                    st.error(f"Error: {r3.text}")
                            else:
                                st.warning("Please enter a response before sending.")

except Exception as e:
    st.error(f"Error connecting to API: {e}")
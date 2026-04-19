import logging
logger = logging.getLogger(__name__)
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Review Reports')

REPORT_URL = "http://web-api:4000/sienna/admin/reports"

reports = []
try:
    response = requests.get(REPORT_URL)
    if response.status_code == 200:
        reports = response.json()
    else:
        st.error(f"Failed to retrieve reports: {response.json().get('error', 'Unknown error')}")
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running")

if reports:
    listing_reports = [r for r in reports if r.get('listingID')]
    user_reports = [r for r in reports if r.get('reportedUserID')]

    st.subheader(f"Reported Listings ({len(listing_reports)})")
    if listing_reports:
        for r in listing_reports:
            with st.expander(f"Report #{r.get('reportID')} — Listing #{r.get('listingID')} | Type: {r.get('reportType', 'N/A')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Report ID:** {r.get('reportID')}")
                    st.write(f"**Listing ID:** {r.get('listingID')}")
                    st.write(f"**Report Type:** {r.get('reportType', 'N/A')}")
                with col2:
                    st.write(f"**Reported By:** {r.get('senderName', 'Unknown')} (ID: {r.get('senderID')})")
                    st.write(f"**Admin ID:** {r.get('adminID', 'Unassigned')}")
                st.write(f"**Reason:** {r.get('reportReason', 'No reason provided')}")
                if st.button(f"Taje action on Report#{r.get('reportID')}", type='primary',use_container_width=True):
                    st.switch_page("pages/30_About.py")
    else:
        st.info("No reported listings.")

    st.divider()

    st.subheader(f"Reported Users ({len(user_reports)})")
    if user_reports:
        for r in user_reports:
            with st.expander(f"Report #{r.get('reportID')} — User #{r.get('reportedUserID')} | Type: {r.get('reportType', 'N/A')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Report ID:** {r.get('reportID')}")
                    st.write(f"**Reported User ID:** {r.get('reportedUserID')}")
                    st.write(f"**Report Type:** {r.get('reportType', 'N/A')}")
                with col2:
                    st.write(f"**Reported By:** {r.get('senderName', 'Unknown')} (ID: {r.get('senderID')})")
                    st.write(f"**Admin ID:** {r.get('adminID', 'Unassigned')}")
                st.write(f"**Reason:** {r.get('reportReason', 'No reason provided')}")
    else:
        st.info("No reported users.")
else:
    if not st.session_state.get("api_error"):
        st.info("No reports found.")

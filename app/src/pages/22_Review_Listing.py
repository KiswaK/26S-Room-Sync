import logging
logger = logging.getLogger(__name__)
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Review Reports')

REPORT_URL = "http://web-api:4000/sienna/admin/reports"
LISTINGS_URL = "http://web-api:4000/sienna/admin/listings"
MODERATION_URL = "http://web-api:4000/sienna/admin/moderation"


# Initialize session state
if 'processed_report_ids' not in st.session_state:
    st.session_state.processed_report_ids = set()
if 'processed_items' not in st.session_state:
    st.session_state.processed_items = []
if 'pending_action' not in st.session_state:
    st.session_state.pending_action = None

# Process any action chosen in the dialog (runs after rerun)
if st.session_state.pending_action:
    pa = st.session_state.pending_action
    st.session_state.processed_report_ids.add(pa['reportID'])
    st.session_state.processed_items.append(pa)
    st.session_state.pending_action = None


@st.dialog("Take Action")
def show_action_options(report):
    # Shrink button text to fit 5 columns
    st.markdown("""
    <style>
    div[data-testid="stDialog"] button p {
        font-size: 9px !important;
        white-space: nowrap;
    }
    </style>
    """, unsafe_allow_html=True)

    target = f"Listing #{report.get('listingID')}" if report.get('listingID') else f"User #{report.get('reportedUserID')}"
    st.markdown(f"**Report #{report['reportID']}** — {target}")
    st.write(f"Reported by: {report.get('senderName', 'Unknown')}  |  Reason: {report.get('reportReason', 'N/A')}")
    st.divider()
    st.markdown("Choose an action:")

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    for action_name, col in [("Suspend", col1), ("Reject", col2), ("Flag", col3), ("Approve", col4), ("Archive", col5), ("Inactive", col6)]:
        with col:
            if st.button(action_name, type='primary', use_container_width=True, key=f"dlg_{action_name}_{report['reportID']}"):
                st.session_state.pending_action = {
                    'reportID': report['reportID'],
                    'listingID': report.get('listingID'),
                    'reportedUserID': report.get('reportedUserID'),
                    'senderID': report.get('senderID'),
                    'action': action_name
                }
                try:
                    response = requests.put(LISTINGS_URL)
                    if response.status_code == 200:
                        st.success(response.json().get("message", "Outdated listings marked inactive"))
                    else:
                        st.error(f"Failed to update listings: {response.json().get('error', response.text or 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to the API: {str(e)}")
                    st.info("Please ensure the API server is running")
                
                try:
                    response = requests.post(MODERATION_URL, json={
                        'reportID': report.get('reportID'),
                        'listingID': report.get('listingID'),
                        'userID': report.get('reportedUserID'),
                        'adminID': report.get('adminID'),
                        'actionType': action_name,
                        'actionReason': None
                    })
                    if response.status_code == 201:
                        st.success(response.json().get("message", "Moderation action logged"))
                    else:
                        st.error(f"Failed to log moderation action: {response.json().get('error', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to the API: {str(e)}")
                    st.info("Please ensure the API server is running")
                
                try:
                    response = requests.put(REPORT_URL, json={
                        'reportID': report.get('reportID'),
                        'listingID': report.get('listingID'),
                        'userID': report.get('reportedUserID'),
                        'adminID': report.get('adminID'),
                        'actionType': action_name,
                        'actionReason': None
                    })
                    if response.status_code == 200:
                        st.success(response.json().get("message", "report status updated"))
                    else:
                        st.error(f"Failed to update listings: {response.json().get('error', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to the API: {str(e)}")
                    st.info("Please ensure the API server is running")
                st.rerun()


# Fetch reports
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

# Filter out already-processed reports
active_reports = [r for r in reports if r.get('reportID') not in st.session_state.processed_report_ids]

if active_reports:
    listing_reports = [r for r in active_reports if r.get('listingID')]
    user_reports = [r for r in active_reports if r.get('reportedUserID') and not r.get('listingID')]

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
                if st.button(f"Take action on Report #{r.get('reportID')}", type='primary',
                             use_container_width=True, key=f"btn_listing_{r.get('reportID')}"):
                    show_action_options(r)
    

    else:
        st.info("No reported listings.")
else:
    st.info("No pending reports.")

st.divider()
st.subheader("Moderation History")
try:
    mod_response = requests.get(MODERATION_URL)
    if mod_response.status_code == 200:
        actions = mod_response.json()
        if actions:
            for a in actions:
                with st.expander(f"Action #{a.get('actionID')} — {a.get('actionType')} on {a.get('actionDate', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Action ID:** {a.get('actionID')}")
                        st.write(f"**Type:** {a.get('actionType')}")
                        st.write(f"**Status:** {a.get('actionStatus', 'N/A')}")
                        st.write(f"**Date:** {a.get('actionDate', 'N/A')}")
                    with col2:
                        st.write(f"**Report ID:** {a.get('reportID', 'N/A')}")
                        st.write(f"**Listing ID:** {a.get('listingID', 'N/A')}")
                        st.write(f"**Target User:** {a.get('targetUserName', 'N/A')} (ID: {a.get('userID', 'N/A')})")
                    if a.get('actionReason'):
                        st.write(f"**Reason:** {a.get('actionReason')}")
        else:
            st.info("No moderation actions recorded yet.")
    else:
        st.error(f"Failed to retrieve moderation history: {mod_response.json().get('error', 'Unknown error')}")
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running")

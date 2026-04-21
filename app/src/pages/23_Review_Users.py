import logging
logger = logging.getLogger(__name__)
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Reported Users')

REPORT_URL = "http://web-api:4000/sienna/admin/reports"
USERS_URL = "http://web-api:4000/sienna/admin/users"
MODERATION_URL = "http://web-api:4000/sienna/admin/moderation"

# Initialize session state
if 'processed_report_ids' not in st.session_state:
    st.session_state.processed_report_ids = set()
if 'processed_items' not in st.session_state:
    st.session_state.processed_items = []
if 'pending_action' not in st.session_state:
    st.session_state.pending_action = None
if 'nav_popup' not in st.session_state:
    st.session_state.nav_popup = None

# Process any action chosen in the dialog (runs after rerun)
if st.session_state.pending_action:
    pa = st.session_state.pending_action
    st.session_state.processed_report_ids.add(pa['reportID'])
    st.session_state.processed_items.append(pa)
    st.session_state.pending_action = None

# Show post-action navigation popup if an action was just completed
if st.session_state.nav_popup:
    nav = st.session_state.nav_popup

    @st.dialog("Action Complete")
    def show_nav_popup():
        st.success(f"Action **{nav['action']}** applied to User #{nav.get('reportedUserID')}.")
        st.write("What would you like to do next?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Go to Processed User List", use_container_width=True, type="primary"):
                st.session_state.nav_popup = None
                st.switch_page("pages/24_View_processed_userList.py")
        with col2:
            if st.button("Stay in Review Users", use_container_width=True):
                st.session_state.nav_popup = None
                st.rerun()

    show_nav_popup()


@st.dialog("Take Action")
def show_action_options(report):
    st.markdown("""
    <style>
    div[data-testid="stDialog"] button p {
        font-size: 13px !important;
        white-space: nowrap;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"**Report #{report['reportID']}** — User #{report.get('reportedUserID')}")
    st.write(f"Reported by: {report.get('senderName', 'Unknown')}  |  Reason: {report.get('reportReason', 'N/A')}")
    st.divider()
    st.markdown("Choose an action:")

    col1, col2, col3, col4, col5 = st.columns(5)
    for action_name, col in [("Suspend", col1), ("Reject", col2), ("Flag", col3), ("Approve", col4), ("Archive", col5)]:
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
                    user_id = report.get('reportedUserID')
                    response = requests.put(f"{USERS_URL}/{user_id}", json={
                        'userStatus': action_name.lower()
                    })
                    if response.status_code == 200:
                        st.success(response.json().get("message", f"User status marked as {action_name}"))
                    else:
                        err = response.json().get('error', 'Unknown error') if response.text else 'Unknown error'
                        st.error(f"Failed to update users status: {err}")
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
                st.session_state.nav_popup = {
                    'action': action_name,
                    'reportedUserID': report.get('reportedUserID'),
                }
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

# Filter out already-processed reports, show only user reports
active_reports = [r for r in reports if r.get('reportID') not in st.session_state.processed_report_ids]
user_reports = [r for r in active_reports if r.get('reportedUserID') and not r.get('listingID')]

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
            if st.button(f"Take action on Report #{r.get('reportID')}", type='primary',
                         use_container_width=True, key=f"btn_user_{r.get('reportID')}"):
                show_action_options(r)
else:
    st.info("No reported users.")

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

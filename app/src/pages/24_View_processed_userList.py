import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Processed Users / Listings')

# Initialize session state in case user lands here directly
if 'processed_report_ids' not in st.session_state:
    st.session_state.processed_report_ids = set()
if 'processed_items' not in st.session_state:
    st.session_state.processed_items = []

items = st.session_state.processed_items

if items:
    # Table header
    header_col1, header_col2, header_col3 = st.columns([3, 2, 1])
    with header_col1:
        st.markdown("**User / Listing**")
    with header_col2:
        st.markdown("**Status**")
    with header_col3:
        st.markdown("**Retrieve**")
    st.divider()

    to_retrieve = None

    for i, pa in enumerate(items):
        if pa.get('listingID'):
            label = f"Listing #{pa['listingID']}"
        elif pa.get('reportedUserID'):
            label = f"User #{pa['reportedUserID']}"
        else:
            label = f"Report #{pa.get('reportID', 'N/A')}"

        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(label)
        with col2:
            st.write(pa.get('action', 'N/A'))
        with col3:
            if st.button("Retrieve", key=f"retrieve_{i}_{pa.get('reportID')}"):
                to_retrieve = i

    # Handle retrieval outside the loop to avoid mutation-during-iteration
    if to_retrieve is not None:
        pa = st.session_state.processed_items.pop(to_retrieve)
        st.session_state.processed_report_ids.discard(pa['reportID'])
        st.rerun()
else:
    st.info("No processed actions yet.")

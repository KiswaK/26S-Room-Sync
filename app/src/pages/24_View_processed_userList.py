import logging
logger = logging.getLogger(__name__)

import pandas as pd
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
    rows = []
    for pa in items:
        if pa.get('listingID'):
            label = f"Listing #{pa['listingID']}"
        elif pa.get('reportedUserID'):
            label = f"User #{pa['reportedUserID']}"
        else:
            label = f"Report #{pa.get('reportID', 'N/A')}"
        rows.append({"User / Listing": label, "Status": pa.get('action', 'N/A'), "Retrieve": False})

    df = pd.DataFrame(rows)

    edited_df = st.data_editor(
        df,
        column_config={
            "Retrieve": st.column_config.CheckboxColumn("Retrieve", default=False)
        },
        disabled=["User / Listing", "Status"],
        hide_index=True,
        use_container_width=True
    )

    # Find checked rows and retrieve them
    to_retrieve = edited_df.index[edited_df["Retrieve"]].tolist()
    if to_retrieve:
        for idx in sorted(to_retrieve, reverse=True):
            pa = st.session_state.processed_items.pop(idx)
            st.session_state.processed_report_ids.discard(pa['reportID'])
        st.rerun()
else:
    st.info("No processed actions yet.")

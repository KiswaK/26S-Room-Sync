import streamlit as st

from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

st.title(f"Welcome, {st.session_state.get('first_name', 'Broker')}")
st.write("Track assigned listings, compare apartment performance, and monitor inquiry demand across your portfolio.")

if st.button("Assigned Listings", type="primary", use_container_width=True):
    st.switch_page("pages/11_Assigned_Listings.py")

if st.button("Market Performance", type="primary", use_container_width=True):
    st.switch_page("pages/12_Market_Performance.py")

if st.button("Inquiries and Workload", type="primary", use_container_width=True):
    st.switch_page("pages/13_Inquiries_Workload.py")
             use_container_width=True):
    st.switch_page('pages/13_Inquiries_Workload.py')

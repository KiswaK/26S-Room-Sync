import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

st.title(f"Welcome, {st.session_state.get('first_name', 'Landlord')}")
st.write("What would you like to do today?")

if st.button('My Listings', type='primary', use_container_width=True):
    st.switch_page('pages/31_My_Listings.py')

if st.button('Inquiries Inbox', type='primary', use_container_width=True):
    st.switch_page('pages/32_Inquiries_Inbox.py')

if st.button('Performance Dashboard', type='primary', use_container_width=True):
    st.switch_page('pages/33_Performance.py')
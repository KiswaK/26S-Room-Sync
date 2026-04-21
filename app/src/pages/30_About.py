import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# About this App")

st.markdown(
    """
    RoomSync is a data-driven rental platform designed to simplify the apartment search process for students and young professionals. By connecting renters, landlords, and brokers in one centralized platform, RoomSync eliminates the need to juggle multiple apps and websites when searching for housing.
    """
)

# Add a button to return to home page
if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")

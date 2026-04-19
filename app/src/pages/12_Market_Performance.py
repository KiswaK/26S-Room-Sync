import streamlit as st

from modules.nav import SideBarLinks
from modules.roomsync import api_request, show_api_error

st.set_page_config(layout="wide")
SideBarLinks()

st.title("Market Performance")

ok, _, payload = api_request("GET", "/ben/brokers/performance")
if ok:
    st.dataframe(payload, use_container_width=True)
else:
    show_api_error(payload)

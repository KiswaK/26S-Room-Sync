import streamlit as st

from modules.nav import SideBarLinks
from modules.roomsync import api_request, show_api_error

st.set_page_config(layout="wide")
SideBarLinks()

broker_id = st.session_state["broker_id"]
st.title("Inquiries and Workload")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Inquiry Demand")
    ok, _, inquiry_payload = api_request("GET", f"/ben/brokers/{broker_id}/inquiries")
    if ok:
        st.dataframe(inquiry_payload, use_container_width=True)
    else:
        show_api_error(inquiry_payload)

with col2:
    st.subheader("Broker Workload")
    ok, _, workload_payload = api_request("GET", "/ben/brokers/workload")
    if ok:
        st.dataframe(workload_payload, use_container_width=True)
    else:
        show_api_error(workload_payload)

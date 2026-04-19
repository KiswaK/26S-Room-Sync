import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

broker_id = st.session_state["broker_id"]
st.title("Inquiries and Workload")
st.write("Monitor renter demand across your listings and compare workload distribution among all brokers.")

API_BASE = "http://web-api:4000/ben"

# fetch
inquiry_data = []
try:
    inq_response = requests.get(f"{API_BASE}/brokers/{broker_id}/inquiries")
    if inq_response.status_code == 200:
        inquiry_data = inq_response.json()
    else:
        st.error(f"Failed to retrieve inquiry data: {inq_response.json().get('error', 'Unknown error')}")
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running")

workload_data = []
try:
    wl_response = requests.get(f"{API_BASE}/brokers/workload")
    if wl_response.status_code == 200:
        workload_data = wl_response.json()
    else:
        st.error(f"Failed to retrieve workload data: {wl_response.json().get('error', 'Unknown error')}")
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")

#inquiry demand
st.header("Inquiry Demand")

if not inquiry_data:
    st.info("No inquiry data found for your listings.")
else:
    inq_df = pd.DataFrame(inquiry_data)

    # summary
    total_inquiries = int(inq_df["totalInquiries"].sum())
    total_listings = len(inq_df)
    avg_per_listing = total_inquiries / total_listings if total_listings > 0 else 0
    zero_inquiry_count = int((inq_df["totalInquiries"] == 0).sum())

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Your Listings", total_listings)
    m2.metric("Total Inquiries", total_inquiries)
    m3.metric("Avg per Listing", f"{avg_per_listing:.1f}")
    m4.metric("Zero-Inquiry Listings", zero_inquiry_count)

    st.divider()

    # bar chart
    st.subheader("Inquiries by Listing")
    chart_df = inq_df[["title", "totalInquiries"]].copy()
    chart_df = chart_df.sort_values("totalInquiries", ascending=False)
    st.bar_chart(chart_df, x="title", y="totalInquiries")

    # priority listing
    if zero_inquiry_count > 0:
        st.subheader("Listings With No Inquiries")
        st.warning("These listings have received zero inquiries and may need attention.")
        no_inq = inq_df[inq_df["totalInquiries"] == 0][["listingID", "title", "status"]]
        st.dataframe(no_inq, use_container_width=True, hide_index=True)

    # all data
    with st.expander("View full inquiry data"):
        st.dataframe(inq_df, use_container_width=True, hide_index=True)

st.divider()

#broker workload
st.header("Broker Workload")

if not workload_data:
    st.info("No workload data available.")
else:
    wl_df = pd.DataFrame(workload_data)

    # current broker
    my_row = wl_df[wl_df["brokerID"] == broker_id]
    if not my_row.empty:
        my_count = int(my_row.iloc[0]["totalListings"])
        avg_count = wl_df["totalListings"].mean()
        st.metric(
            "Your Assigned Listings",
            my_count,
            delta=f"{my_count - avg_count:+.0f} vs avg",
        )

    # bar chart
    st.subheader("Listings per Broker")
    wl_chart = wl_df[["brokerName", "totalListings"]].copy()
    wl_chart = wl_chart.sort_values("totalListings", ascending=False)
    st.bar_chart(wl_chart, x="brokerName", y="totalListings")

    # all data
    with st.expander("View full workload data"):
        st.dataframe(wl_df, use_container_width=True, hide_index=True)

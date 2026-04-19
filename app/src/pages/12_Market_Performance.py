import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

broker_id = st.session_state["broker_id"]
st.title("Market Performance")
st.write("Compare views, applications, and interest levels across all apartments on the platform.")

API_BASE = "http://web-api:4000/ben"

#fetch
performance = []
try:
    response = requests.get(f"{API_BASE}/brokers/performance")
    if response.status_code == 200:
        performance = response.json()
    else:
        st.error(f"Failed to retrieve performance data: {response.json().get('error', 'Unknown error')}")
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running")

if not performance:
    st.info("No performance data available yet.")
    st.stop()

df = pd.DataFrame(performance)

#Summary
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Apartments", len(df))
col2.metric("Avg Views", f"{df['viewCount'].mean():.0f}")
col3.metric("Avg Applications", f"{df['applicationsCount'].mean():.0f}")
col4.metric("Avg Days on Market", f"{df['daysOnMarket'].mean():.0f}")

st.divider()


st.subheader("Interest Level Breakdown")
interest_counts = df["interestLevel"].value_counts().reset_index()
interest_counts.columns = ["Interest Level", "Count"]
st.bar_chart(interest_counts, x="Interest Level", y="Count")

st.divider()


st.subheader("Detailed Performance Data")
filter_level = st.selectbox(
    "Filter by interest level",
    ["All", "High Interest", "Moderate Interest", "Low Interest"],
)

if filter_level != "All":
    filtered = df[df["interestLevel"] == filter_level]
else:
    filtered = df

st.dataframe(
    filtered[["unitNumber", "brokerName", "viewCount", "applicationsCount",
              "occupancyRate", "daysOnMarket", "interestLevel"]],
    use_container_width=True,
    hide_index=True,
)

st.divider()


st.subheader("Views vs Applications")
chart_data = filtered[["unitNumber", "viewCount", "applicationsCount"]].copy()
chart_data = chart_data.set_index("unitNumber")
st.scatter_chart(chart_data, x="viewCount", y="applicationsCount")

st.divider()


st.subheader("Your Listings by Status")
try:
    status_response = requests.get(f"{API_BASE}/brokers/{broker_id}/listings-by-status")
    if status_response.status_code == 200:
        status_data = status_response.json()
        if status_data:
            status_df = pd.DataFrame(status_data)
            st.bar_chart(status_df, x="status", y="totalListings")
            st.dataframe(status_df, use_container_width=True, hide_index=True)
        else:
            st.info("No status data available.")
    else:
        st.error(f"Failed to retrieve status data: {status_response.json().get('error', 'Unknown error')}")
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")

st.divider()

st.subheader("Log a Performance Report")
st.write("Record a snapshot of an apartment's current performance metrics.")

with st.form("create_report_form"):
    report_apt_id = st.number_input("Apartment ID", min_value=1, step=1)
    report_views = st.number_input("View Count", min_value=0, step=1, value=0)
    report_apps = st.number_input("Applications Count", min_value=0, step=1, value=0)
    report_occupancy = st.number_input("Occupancy Rate (%)", min_value=0.0, max_value=100.0, step=0.5, value=0.0)
    report_days = st.number_input("Days on Market", min_value=0, step=1, value=0)
    submit_report = st.form_submit_button("Create Report")

if submit_report:
    try:
        response = requests.post(
            f"{API_BASE}/brokers/{broker_id}/reports",
            json={
                "apartmentID": int(report_apt_id),
                "viewCount": int(report_views),
                "applicationsCount": int(report_apps),
                "occupancyRate": float(report_occupancy),
                "daysOnMarket": int(report_days),
            },
        )
        if response.status_code == 201:
            result = response.json()
            st.success(f"Report created (ID: {result.get('reportID', 'N/A')})")
            st.rerun()
        else:
            st.error(f"Failed to create report: {response.json().get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the API: {str(e)}")

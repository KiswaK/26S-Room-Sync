from datetime import datetime, date

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

broker_id = st.session_state["broker_id"]
st.title("Assigned Listings")

API_BASE = "http://web-api:4000/ben"

# ── Helper to parse dates from the API ──────────────────────────────
def parse_date(value):
    """Handle both '2025-04-04' and 'Fri, 04 Apr 2025 00:00:00 GMT' formats."""
    if not value:
        return date.today()
    s = str(value)
    # Try ISO format first (2025-04-04)
    try:
        return date.fromisoformat(s)
    except ValueError:
        pass
    # Try HTTP date format (Fri, 04 Apr 2025 00:00:00 GMT)
    try:
        return datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %Z").date()
    except ValueError:
        pass
    return date.today()

# ── Fetch listings ──────────────────────────────────────────────────
listings = []
try:
    response = requests.get(f"{API_BASE}/brokers/{broker_id}/listings")
    if response.status_code == 200:
        listings = response.json()
    else:
        st.error(f"Failed to retrieve listings: {response.json().get('error', 'Unknown error')}")
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running")

if not listings:
    st.info("This broker has no assigned listings.")
    st.stop()

st.dataframe(listings, use_container_width=True, hide_index=True)

# ── Select a listing to edit ────────────────────────────────────────
listing_options = {f"{item['listingID']} - {item['title']}": item for item in listings}
selected_key = st.selectbox("Choose listing", list(listing_options.keys()))
selected_listing = listing_options[selected_key]

# ── Update form (PUT) ───────────────────────────────────────────────
with st.form("broker_update_form"):
    updated_title = st.text_input("Title", value=selected_listing["title"])
    updated_status = st.selectbox(
        "Status",
        ["available", "inactive", "rented", "archived"],
        index=["available", "inactive", "rented", "archived"].index(selected_listing["status"])
        if selected_listing["status"] in ["available", "inactive", "rented", "archived"]
        else 0,
    )
    updated_date = st.date_input(
        "Available date",
        value=parse_date(selected_listing["availableDate"]),
    )
    updated_fee = st.number_input(
        "Broker fee",
        min_value=0.0,
        step=50.0,
        value=float(selected_listing["brokerFee"] or 0),
    )
    save_button = st.form_submit_button("Update Listing")

    if save_button:
        try:
            response = requests.put(
                f"{API_BASE}/brokers/{broker_id}/listings/{selected_listing['listingID']}",
                json={
                    "title": updated_title,
                    "status": updated_status,
                    "availableDate": str(updated_date),
                    "brokerFee": updated_fee,
                },
            )
            if response.status_code == 200:
                st.success("Listing updated.")
                st.rerun()
            else:
                st.error(f"Failed to update listing: {response.json().get('error', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the API: {str(e)}")

# ── Remove listing (DELETE) ─────────────────────────────────────────
if st.button("Remove Listing From My Portfolio", type="primary"):
    try:
        response = requests.delete(
            f"{API_BASE}/brokers/{broker_id}/listings/{selected_listing['listingID']}",
        )
        if response.status_code == 200:
            st.success("Listing removed from broker portfolio.")
            st.rerun()
        else:
            st.error(f"Failed to remove listing: {response.json().get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the API: {str(e)}")

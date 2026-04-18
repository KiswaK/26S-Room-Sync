from datetime import date

import streamlit as st

from modules.nav import SideBarLinks
from modules.roomsync import api_request, show_api_error

st.set_page_config(layout="wide")
SideBarLinks()

broker_id = st.session_state["broker_id"]
st.title("Assigned Listings")

ok, _, payload = api_request("GET", f"/ben/brokers/{broker_id}/listings")
if not ok:
    show_api_error(payload)
    listings = []
else:
    listings = payload

st.dataframe(listings, use_container_width=True)

listing_options = {f"{item['listingID']} - {item['title']}": item for item in listings}

if listing_options:
    selected_key = st.selectbox("Choose listing", list(listing_options.keys()))
    selected_listing = listing_options[selected_key]

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
            value=date.fromisoformat(str(selected_listing["availableDate"])),
        )
        updated_fee = st.number_input(
            "Broker fee",
            min_value=0.0,
            step=50.0,
            value=float(selected_listing["brokerFee"] or 0),
        )
        save_button = st.form_submit_button("Update Listing")

    if save_button:
        ok, _, response_payload = api_request(
            "PUT",
            f"/ben/brokers/{broker_id}/listings/{selected_listing['listingID']}",
            json={
                "title": updated_title,
                "status": updated_status,
                "availableDate": str(updated_date),
                "brokerFee": updated_fee,
            },
        )
        if ok:
            st.success("Listing updated.")
            st.rerun()
        else:
            show_api_error(response_payload)

    if st.button("Remove Listing From My Portfolio", type="primary"):
        ok, _, response_payload = api_request(
            "DELETE",
            f"/ben/brokers/{broker_id}/listings/{selected_listing['listingID']}",
        )
        if ok:
            st.success("Listing removed from broker portfolio.")
            st.rerun()
        else:
            show_api_error(response_payload)
else:
    st.info("This broker has no assigned listings.")

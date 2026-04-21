import logging
import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

landlord_id = st.session_state['landlord_id']
API = "http://web-api:4000"

st.title("My Listings")

# Create new listing
with st.expander("➕ Create New Listing"):
    unit_number = st.text_input("Unit Number")
    apt_id     = st.number_input("Apartment ID", min_value=1, step=1)
    avail_date = st.date_input("Available Date")
    broker_fee = st.number_input("Broker Fee ($)", min_value=0.0, step=50.0)
    
    if st.button("Create Listing"):
        payload = {
            "unitNumber":         unit_number,
            "apartmentID":   apt_id,
            "availableDate": str(avail_date),
            "brokerFee":     broker_fee
        }
        r = requests.post(f"{API}/marcus/landlord/{landlord_id}/listings", json=payload)
        if r.status_code == 201:
            st.success("Listing created!")
        else:
            st.error(f"Error: {r.text}")

# View existing listings
st.subheader("Current Listings")
try:
    r = requests.get(f"{API}/marcus/landlord/{landlord_id}/listings")
    listings = r.json()
    
    if not listings:
        st.info("No listings found.")
    else:
        for listing in listings:
            with st.expander(f"Unit {listing['unitNumber']} — {listing['status']}"):
                st.write(f"**Available:** {listing['availableDate']}")
                st.write(f"**Broker Fee:** ${listing['brokerFee']}")
                
                # Update status
                new_status = st.selectbox(
                    "Update Status",
                    ["available", "rented", "archived"],
                    key=f"status_{listing['listingID']}"
                )
                if st.button("Update Status", key=f"update_{listing['listingID']}"):
                    r2 = requests.put(
                        f"{API}/marcus/landlord/{landlord_id}/listings/{listing['listingID']}/status",
                        json={"status": new_status}
                    )
                    if r2.status_code == 200:
                        st.success("Status updated!")
                    else:
                        st.error(f"Error: {r2.text}")
                
                # Delete listing
                if st.button("🗑️ Delete Listing", key=f"delete_{listing['listingID']}"):
                    r3 = requests.delete(
                        f"{API}/marcus/landlord/{landlord_id}/listings/{listing['listingID']}"
                    )
                    if r3.status_code == 200:
                        st.success("Listing deleted!")
                    else:
                        st.error(f"Error: {r3.text}")

except Exception as e:
    st.error(f"Error connecting to API: {e}")
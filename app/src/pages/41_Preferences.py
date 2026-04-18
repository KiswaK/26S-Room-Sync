import datetime
import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Initialize sidebar
SideBarLinks()

st.title("Set Apartment Search Preferences")

# Initialize session state for modal
if "show_success_modal" not in st.session_state:
    st.session_state.show_success_modal = False
if "reset_form" not in st.session_state:
    st.session_state.reset_form = False
if "form_key_counter" not in st.session_state:
    st.session_state.form_key_counter = 0

# Define the success dialog function
@st.dialog("Success")
def show_success_dialog():
    st.markdown(f"### Your preferences have been successfully added to the system!")
    
    # Create two buttons side by side
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Return Home", use_container_width=True):
            st.session_state.show_success_modal = False
            st.switch_page("pages/40_Renter_Home.py")
    
    with col2:
        if st.button("Continue Editing", use_container_width=True):
            st.session_state.show_success_modal = False
            st.session_state.reset_form = True
            st.rerun()

# Handle form reset
if st.session_state.reset_form:
    st.session_state.form_key_counter += 1
    st.session_state.reset_form = False

# API endpoint
PREFERENCES_URL = f"http://web-api:4000/samuel/renters/{st.session_state['renter_id']}/preferences"
DEALBREAKERS_URL = f"http://web-api:4000/samuel/renters/{st.session_state['renter_id']}/deal_breakers"

# get the existing prefs and dealbreakers
try:
    pref_response = requests.get(PREFERENCES_URL)
    if pref_response.status_code == 200:
        existing_prefs = pref_response.json()
    else:
        st.error(f"Failed to retrieve existing preferences: {pref_response.json().get('error', 'Unknown error')}")
        existing_prefs = {}
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running")
    existing_prefs = {}
try:
    dealbreaker_response = requests.get(DEALBREAKERS_URL)
    if dealbreaker_response.status_code == 200:
        existing_dealbreakers = dealbreaker_response.json()
    else:
        st.error(f"Failed to retrieve existing dealbreakers: {dealbreaker_response.json().get('error', 'Unknown error')}")
        existing_dealbreakers = {}
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running")
    existing_dealbreakers = {}

def get_default_value(feature, constructor=lambda x: x):
    for item in existing_dealbreakers:
        if item['label'] == feature:
            return constructor(item['value'])
    for item in existing_prefs:
        if item['label'] == feature:
            return constructor(item['value'])
    return None

def is_dealbreaker(feature):
    for item in existing_dealbreakers:
        if item['label'] == feature:
            return True
    return False

def str_to_bool(s):
    return s == '1'

# Create a form 
with st.form(f"set_prefs_form_{st.session_state.form_key_counter}"):
    st.subheader("Apartment Preferences")

    # Required fields
    col_rent, col_rent_db = st.columns([4, 1])
    with col_rent:
        max_rent = st.number_input("Maximum Rent ($)", min_value=0.0, value=get_default_value("max_rent", float))
    with col_rent_db:
        st.markdown("<br>", unsafe_allow_html=True)
        rent_dealbreaker = st.toggle("Dealbreaker", key="rent_dealbreaker", value=is_dealbreaker("max_rent"))

    col_bed, col_bed_db = st.columns([4, 1])
    with col_bed:
        bedrooms = st.number_input("Number of Bedrooms", min_value=0, value=get_default_value("bedrooms", int))
    with col_bed_db:
        st.markdown("<br>", unsafe_allow_html=True)
        bedrooms_dealbreaker = st.toggle("Dealbreaker", key="bedrooms_dealbreaker", value=is_dealbreaker("bedrooms"))

    col_bath, col_bath_db = st.columns([4, 1])
    with col_bath:
        bathrooms = st.number_input("Number of Bathrooms", min_value=0.0, value=get_default_value("bathrooms", float))
    with col_bath_db:
        st.markdown("<br>", unsafe_allow_html=True)
        bathrooms_dealbreaker = st.toggle("Dealbreaker", key="bathrooms_dealbreaker", value=is_dealbreaker("bathrooms"))

    st.markdown("**Amenities**")

    col_closet, col_closet_db = st.columns([4, 1])
    with col_closet:
        walk_in_closet = st.checkbox("Walk-in Closet", key="walk_in_closet", value=get_default_value("walk_in_closet", str_to_bool))
    with col_closet_db:
        walk_in_closet_dealbreaker = st.toggle("Dealbreaker", key="walk_in_closet_dealbreaker", value=is_dealbreaker("walk_in_closet"))

    col_dish, col_dish_db = st.columns([4, 1])
    with col_dish:
        dishwasher = st.checkbox("Dishwasher", key="dishwasher", value=get_default_value("dishwasher", str_to_bool))
    with col_dish_db:
        dishwasher_dealbreaker = st.toggle("Dealbreaker", key="dishwasher_dealbreaker", value=is_dealbreaker("dishwasher"))

    col_laundry, col_laundry_db = st.columns([4, 1])
    with col_laundry:
        in_unit_laundry = st.checkbox("In-unit Laundry", key="in_unit_laundry", value=get_default_value("in_unit_laundry", str_to_bool))
    with col_laundry_db:
        in_unit_laundry_dealbreaker = st.toggle("Dealbreaker", key="in_unit_laundry_dealbreaker", value=is_dealbreaker("in_unit_laundry"))

    col_parking, col_parking_db = st.columns([4, 1])
    with col_parking:
        parking = st.checkbox("Parking", key="parking", value=get_default_value("parking", str_to_bool))
    with col_parking_db:
        parking_dealbreaker = st.toggle("Dealbreaker", key="parking_dealbreaker", value=is_dealbreaker("parking"))

    col_ac, col_ac_db = st.columns([4, 1])
    with col_ac:
        ac = st.checkbox("AC", key="ac", value=get_default_value("ac", str_to_bool))
    with col_ac_db:
        ac_dealbreaker = st.toggle("Dealbreaker", key="ac_dealbreaker", value=is_dealbreaker("ac"))

    col_pets, col_pets_db = st.columns([4, 1])
    with col_pets:
        allows_pets = st.radio("Allows Pets?", options=["Yes", "No"], index=0 if get_default_value("allows_pets", str_to_bool) else 1)
    with col_pets_db:
        st.markdown("<br>", unsafe_allow_html=True)
        pets_dealbreaker = st.toggle("Dealbreaker", key="pets_dealbreaker", value=is_dealbreaker("allows_pets"))
    # Form submission button
    submitted = st.form_submit_button("Submit Preferences")

    if submitted:
        # Prepare the data for API
        pref_data = {}
        dealbreaker_data = {}
        
        if max_rent is not None:
            if rent_dealbreaker:
                dealbreaker_data["max_rent"] = max_rent
            else:
                pref_data["max_rent"] = max_rent
        
        if bedrooms is not None:
            if bedrooms_dealbreaker:
                dealbreaker_data["bedrooms"] = bedrooms
            else:
                pref_data["bedrooms"] = bedrooms
        
        if bathrooms is not None:
            if bathrooms_dealbreaker:
                dealbreaker_data["bathrooms"] = bathrooms
            else:
                pref_data["bathrooms"] = bathrooms
        
        if walk_in_closet:
            if walk_in_closet_dealbreaker:
                dealbreaker_data["walk_in_closet"] = True
            else:
                pref_data["walk_in_closet"] = True
        
        if dishwasher:
            if dishwasher_dealbreaker:
                dealbreaker_data["dishwasher"] = True
            else:
                pref_data["dishwasher"] = True
        
        if in_unit_laundry:
            if in_unit_laundry_dealbreaker:
                dealbreaker_data["in_unit_laundry"] = True
            else:
                pref_data["in_unit_laundry"] = True
        
        if parking:
            if parking_dealbreaker:
                dealbreaker_data["parking"] = True
            else:
                pref_data["parking"] = True
        
        if ac:
            if ac_dealbreaker:
                dealbreaker_data["ac"] = True
            else:
                pref_data["ac"] = True
        
        if allows_pets:
            allows_pets_value = True if allows_pets == "Yes" else False
            if pets_dealbreaker:
                dealbreaker_data["allows_pets"] = allows_pets_value
            else:
                pref_data["allows_pets"] = allows_pets_value

        try:
            # Send PUT   request to API
            response = requests.put(PREFERENCES_URL, json=pref_data)

            if response.status_code != 201:
                st.error(
                    f"Failed to add update preferences: {response.json().get('error', 'Unknown error')}"
                )

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the API: {str(e)}")
            st.info("Please ensure the API server is running")
            
        try:
            # Send PUT request to API
            response = requests.put(DEALBREAKERS_URL, json=dealbreaker_data)

            if response.status_code == 201:
                st.session_state.show_success_modal = True
                st.rerun()
            else:
                st.error(
                    f"Failed to add update preferences: {response.json().get('error', 'Unknown error')}"
                )

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the API: {str(e)}")
            st.info("Please ensure the API server is running")

# Show success modal if preferences were successfully set
if st.session_state.show_success_modal:
    show_success_dialog()

# Add a button to return to Home
if st.button("Return Home"):
    st.switch_page("pages/40_Renter_Home.py")

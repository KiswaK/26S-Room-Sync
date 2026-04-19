# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has functions to add links to the left sidebar based on the user's role.

import streamlit as st


# ---- General ----------------------------------------------------------------

def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def about_page_nav():
    st.sidebar.page_link("pages/30_About.py", label="About", icon="🧠")


# ---- Role: pol_strat_advisor ------------------------------------------------

def pol_strat_home_nav():
    st.sidebar.page_link(
        "pages/00_Pol_Strat_Home.py", label="Political Strategist Home", icon="👤"
    )


def world_bank_viz_nav():
    st.sidebar.page_link(
        "pages/01_World_Bank_Viz.py", label="World Bank Visualization", icon="🏦"
    )


def map_demo_nav():
    st.sidebar.page_link("pages/02_Map_Demo.py", label="Map Demonstration", icon="🗺️")


# ---- Role: usaid_worker -----------------------------------------------------

def usaid_worker_home_nav():
    st.sidebar.page_link(
        "pages/10_Broker_Home.py", label="Broker Home", icon="🏠"
    )


def ngo_directory_nav():
    st.sidebar.page_link("pages/14_NGO_Directory.py", label="NGO Directory", icon="📁")


def add_ngo_nav():
    st.sidebar.page_link("pages/15_Add_NGO.py", label="Add New NGO", icon="➕")


def prediction_nav():
    st.sidebar.page_link(
        "pages/11_Assigned_Listings.py", label="Assigned Listing", icon="📈"
    )


def api_test_nav():
    st.sidebar.page_link("pages/12_Market_Performance.py", label="Market Performance", icon="🛜")


def classification_nav():
    st.sidebar.page_link(
        "pages/13_Inquiries_Workload.py", label="Inquiries Workload", icon="🌺"
    )


# ---- Role: administrator ----------------------------------------------------

def admin_home_nav():
    st.sidebar.page_link("pages/20_Admin_Home.py", label="System Admin Homepage", icon="🖥️")

def review_listings_nav():
    st.sidebar.page_link(
        "pages/22_Review_Listing.py", label="Listings", icon="🗒️"
    )

def review_users_nav():
    st.sidebar.page_link(
        "pages/23_Review_Users.py", label="Users", icon="👤"
    )

def view_processed_user_listing():
    st.sidebar.page_link(
        "pages/24_View_processed_userList.py", label="Processed User/Listings", icon="📋"
    )

# ---- Role: renter -----------------------------------------------------------
def renter_home_nav():
    st.sidebar.page_link("pages/40_Renter_Home.py", label="Renter Home", icon="👤")

def set_preferences_nav():
    st.sidebar.page_link(
        "pages/41_Preferences.py", label="Set Preferences", icon="⚙️"
    )

def inquiries_nav():
    st.sidebar.page_link(
        "pages/42_Inquiries.py", label="View/Send Inquiries", icon="📬"
    )

def classmate_listings_nav():
    st.sidebar.page_link(
        "pages/43_Classmate_Listings.py", label="Classmate Listings", icon="🎓"
    )

# ---- Sidebar assembly -------------------------------------------------------

def SideBarLinks(show_home=False):
    """
    Renders sidebar navigation links based on the logged-in user's role.
    The role is stored in st.session_state when the user logs in on Home.py.
    """

    # Logo appears at the top of the sidebar on every page
    st.sidebar.image("assets/logo.png", width=150)

    # If no one is logged in, send them to the Home (login) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        home_nav()

    if st.session_state["authenticated"]:

        if st.session_state["role"] == "pol_strat_advisor":
            pol_strat_home_nav()
            world_bank_viz_nav()
            map_demo_nav()

        if st.session_state["role"] == "usaid_worker":
            usaid_worker_home_nav()
            ngo_directory_nav()
            add_ngo_nav()
            prediction_nav()
            api_test_nav()
            classification_nav()

        if st.session_state["role"] == "administrator":
            admin_home_nav()
            review_listings_nav()
            review_users_nav()
            view_processed_user_listing()
        
        if st.session_state["role"] == "renter":
            renter_home_nav()
            set_preferences_nav()
            inquiries_nav()
            classmate_listings_nav()

    # About link appears at the bottom for all roles
    about_page_nav()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")

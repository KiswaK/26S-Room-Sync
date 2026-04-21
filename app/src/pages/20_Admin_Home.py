import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Hi, Sienna 👋')
st.write('### What would you like to do today?')

if st.button('Review listings',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/22_Review_Listing.py')

if st.button('Review users',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/23_Review_Users.py')

if st.button('View processed users/listings',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/24_View_processed_userList.py')

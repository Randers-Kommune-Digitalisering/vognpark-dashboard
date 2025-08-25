import streamlit as st
from page.vognpark import get_vognpark_overview

st.set_page_config(page_title="Randers Kommune Vognpark Dashboard", page_icon="assets/favicon.ico")

get_vognpark_overview()

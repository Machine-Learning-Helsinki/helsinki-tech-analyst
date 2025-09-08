import streamlit as st
from datetime import date
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_pipeline.storage import connect_storage, get_data

# Page config
st.set_page_config(
    page_title="Helsinki Tech Analysis",
    page_icon="📊",
    layout="wide"
)

# Database connection
@st.cache_resource
def init_connection():
    return connect_storage()

# Data loading
@st.cache_data
def load_data():
    conn = init_connection()
    return get_data(conn=conn)

# Main app
st.title("Helsinki Tech Analysis Dashboard")
st.write("Real-time analysis of tech job market in Helsinki")

# Load data
try:
    data = load_data()
    st.dataframe(data)
except Exception as e:
    st.error(f"Error loading data: {e}")

def convert_date(d):
    try:
        return d.date()
    except Exception as e:
        st.warning(f"Date conversion error: {e}")
        return None
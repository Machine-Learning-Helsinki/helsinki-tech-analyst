import streamlit as st
from datetime import date
import sys
import os

# Add parent directory to path for imports
# This assumes your project structure is like:
# my_project/
# ├── data_pipeline/
# │   └── storage.py
# └── streamlit_app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure data_pipeline.storage exists and contains connect_storage and get_data
# Placeholder for data_pipeline.storage functions if they don't exist for testing purposes
try:
    from data_pipeline.storage import connect_storage, get_data
except ImportError:
    st.error("Could not import data_pipeline.storage. Please ensure the module exists and is accessible.")
    st.stop() # Stop the app if essential imports fail


# --- Database Connection and Data Retrieval ---
try:
    conn = connect_storage()
    # cur = conn.cursor() # 'cur' is not used, so it can be removed
    data = get_data(conn=conn)
    if not data:
        st.warning("No data retrieved from the database. Displaying empty charts.")
except Exception as e:
    st.error(f"Failed to connect to database or retrieve data: {e}")
    st.stop() # Stop the app if data retrieval fails


# --- Streamlit Display - Data Overview ---
st.title("Data from Database")
st.write("This is a simple Streamlit app to display data from the database.")
st.subheader("Data Overview")
st.write("Here is the data retrieved from the database:")
# Ensure data is in a format st.dataframe can handle, e.g., list of lists/tuples or pandas DataFrame
st.dataframe(data)

# --- Helper Function (Unused in current code, but kept) ---
def convert_date(d):
    """
    Converts a datetime object to a date object.
    This function is defined but not directly called in the provided code.
    """
    try:
        if hasattr(d, 'date'): # Check if it's a datetime object
            return d.date()
        return d # Assume it's already a date or not convertible
    except Exception as e:
        print(f"ERROR: Failed to convert date - {e}")
        return None

# --- Function to Count Articles Per Day ---
def count_articles_per_day(data):
    """
    Counts the number of articles per day from the provided data.
    Assumes the date/datetime object is at index 4 of each data item.
    """
    try:
        time_dict = {}
        for d_item in data:
            # Assuming d_item[4] is a datetime object
            if len(d_item) > 4 and d_item[4]: # Basic check for index and not None
                only_date = d_item[4].date()
                time_dict[only_date] = time_dict.get(only_date, 0) + 1

        # Sort dates for better chart display (optional but good practice)
        sorted_dates = sorted(time_dict.keys())
        sorted_counts = [time_dict[d] for d in sorted_dates]

        return {"Date": sorted_dates, "Number of Articles": sorted_counts}
    except Exception as e:
        st.error(f"ERROR: Failed to count articles per day - {e}")
        return {"Date": [], "Number of Articles": []}

# --- CORRECTED Function to Filter Data by Source ---
def filter_data_by_source(data):
    """
    Counts the number of articles per source from the provided data.
    Assumes the source string is at index 1 of each data item.
    """
    try:
        source_counts = {}
        for d_item in data:
            # Assuming d_item[1] is the source string
            if len(d_item) > 1 and d_item[1]: # Basic check for index and not None
                source = d_item[1]
                source_counts[source] = source_counts.get(source, 0) + 1

        # Convert dictionary to the format expected by st.bar_chart
        # Sort sources alphabetically for consistent chart display (optional)
        sorted_sources = sorted(source_counts.keys())
        sorted_counts = [source_counts[s] for s in sorted_sources]

        return {"Source": sorted_sources, "Number of Articles": sorted_counts}
    except Exception as e:
        st.error(f"ERROR: Failed to count articles by source - {e}")
        return {"Source": [], "Number of Articles": []}

# --- Streamlit Display - Charts ---
st.title("Number of Articles Over Time")
st.bar_chart(data=count_articles_per_day(data), x='Date', y='Number of Articles', use_container_width=True)
print("INFO: Displayed number of articles over time.")

st.title("Number of Articles by Source")
st.bar_chart(data=filter_data_by_source(data), x='Source', y='Number of Articles', use_container_width=True)
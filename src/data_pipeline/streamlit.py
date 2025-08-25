from storage import connect_storage, store_data, get_data
import streamlit as st

# from ..data_pipeline.main import run_pipeline

conn = connect_storage()
data = get_data(conn=conn)


st.title("Data from Database")
st.write("This is a simple Streamlit app to display data from the database.")
st.subheader("Data Overview")
st.write("Here is the data retrieved from the database:")
st.dataframe(data)



st.bar_chart(data=data, x=1, y=2, use_container_width=True,horizontal=True, height=500)

from storage import connect_storage, store_data, get_data
import streamlit as st
from datetime import date

# from ..data_pipeline.main import run_pipeline

conn = connect_storage()
cur = conn.cursor()
data = get_data(conn=conn)





st.title("Data from Database")
st.write("This is a simple Streamlit app to display data from the database.")
st.subheader("Data Overview")
st.write("Here is the data retrieved from the database:")
st.dataframe(data)


time = []
for d in data:
    time.append(d[7])

time_dict = {}
for t in time : 
    only_date = t.date()
    print(only_date)
    if only_date in time_dict:
        time_dict[only_date] += 1
    else:
        time_dict[only_date] = 1


print(time_dict)


time_dict = {"Date": list(time_dict.keys()), "Number of Articles": list(time_dict.values())} 


st.title("Number of Articles Over Time")
st.bar_chart(data=time_dict,x='Date',y='Number of Articles',use_container_width=True)



    




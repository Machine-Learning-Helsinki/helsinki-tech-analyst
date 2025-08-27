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

def convert_date(d):
    try:
        return d.date()
    except Exception as e:
        print(f"ERROR: Failed to convert date - {e}")
        return None


def count_articles_per_day(data):
    try:
        time = []
        for d in data:
            time.append(d[4])

        time_dict = {}
        for t in time : 
            only_date = t.date()
            if only_date in time_dict:
                time_dict[only_date] += 1
            else:
                time_dict[only_date] = 1



        time_dict = {"Date": list(time_dict.keys()), "Number of Articles": list(time_dict.values())}
        return time_dict
    except Exception as e:
        print(f"ERROR: Failed to count articles per day - {e}")
        return {"Date": [], "Number of Articles": []}

def filter_data_by_source(data):
    articlesTotalSources = {}
    sources = []
    Number_of_articles_per_source = []
    for d in data:
        source = d[1]
        l = sources.split(",")
        print(l)
        if source not in sources:
            sources.append(source)
            Number_of_articles_per_source.append(1)
        else:
            index = sources.index(source)
            Number_of_articles_per_source[index] += 1
    articlesTotalSources = {"Source": sources, "Number of Articles": Number_of_articles_per_source}
    return articlesTotalSources


            
        
    sources = list(set(sources))




st.title("Number of Articles Over Time")
st.bar_chart(data=count_articles_per_day(data),x='Date',y='Number of Articles',use_container_width=True)

print("INFO: Displayed number of articles over time.")
st.title("Number of Articles by Source")

st.bar_chart(data=filter_data_by_source(data),x='Source',y='Number of Articles',use_container_width=True)


    




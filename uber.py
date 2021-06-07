import pandas as pd
import pandas_profiling as pf
import streamlit as st

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')


@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    def lowercase(x): return str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


data = load_data(100)
st.subheader('Raw Data')
st.write(data)
x = st.slider('x')
st.write(x, 'Squared is :', x*x)
selectbox_label = st.selectbox('Filter to :', ['lat', 'lon'])
selected_columns = selectbox_label
st.write(data[selected_columns])
report = pf.ProfileReport(data)
st.write(report)
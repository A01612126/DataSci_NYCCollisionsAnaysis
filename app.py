#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_PATH = ("/Users/angelgonzaleztorres/Desktop/data_Science_web/Motor_Vehicle_Collisions_-_Crashes_20240309.csv")
st.title("Motor Vehicle Collisions in NYC")
st.markdown('''This application is a streamlit dashboard that can be used 
            to analyze motor-vehicle incidents in New York City 🗽💥🚗''')

@st.cache_data(persist = True)
def load_data(nrows):
    data = pd.read_csv(DATA_PATH, nrows = nrows, parse_dates=[['CRASH DATE','CRASH TIME']])
    data.dropna(subset=["LATITUDE","LONGITUDE"],inplace = True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data.rename(columns={'crash date_crash time':'date_time'}, inplace=True)
    return data

data = load_data(100000)
original_data = data

st.header("Where do most injuries happen in NYC?")
injured_people = st.slider("Number of injured people",0,19)
st.map(data.query(" `number of persons injured` >= @injured_people")[["latitude","longitude"]].dropna(how="any"))

st.header("Collisions at a given hour")
hour = st.slider("Hour", 0, 23)
data= data[data['date_time'].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" %(hour,(hour+1)%24))
midpoint = (np.average(data['latitude']),np.average(data['longitude']))
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude":midpoint[0],
        "longitude": midpoint[1],
        "zoom":10,
        "pitch":60,
    },
    layers = [
        pdk.Layer(
            "HexagonLayer",
            data=data[['date_time','latitude','longitude']],
            get_position=['longitude','latitude'],
            radius=100,
            extruded= True,
            pickable = True,
            elevation_scale=4,
            elevation_range= [0, 1000],
            ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" %(hour, (hour+1)%24))
filtered = data[
    (data['date_time'].dt.hour >= hour) & (data['date_time'].dt.hour < (hour+1))
]
hist = np.histogram(filtered['date_time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute':range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute',y='crashes', hover_data=['minute','crashes'],height=400)
st.write(fig)


st.header("Most dangerous streets by affected type")
select = st.selectbox('Affected Type', ['Pedestrians','Cyclist','Motorist'])
if select =="Pedestrians":
    st.write(original_data.query('`number of pedestrians injured` >=1')[['on street name','number of pedestrians injured']].sort_values(by=['number of pedestrians injured'],ascending = False).dropna(how="any")[:5])
elif select =="Cyclist":
    st.write(original_data.query('`number of cyclist injured` >=1')[['on street name','number of cyclist injured']].sort_values(by=['number of cyclist injured'],ascending = False).dropna(how="any")[:5])
else:
    st.write(original_data.query('`number of motorist injured` >=1')[['on street name','number of motorist injured']].sort_values(by=['number of motorist injured'],ascending = False).dropna(how="any")[:5])


if st.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(data)

    

# In[ ]:



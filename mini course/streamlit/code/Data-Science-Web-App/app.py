import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = ("Motor_Vehicle_Collisions_-_Crashes.csv")

st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application s a streamlit dashboard that can be used to analyze motor Vehicle Collisions in NYC 🗽")

def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates= [['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data

data = load_data(100000)
original_data = data

st.header("Where are most people injured in nyc")
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 19)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collision between %i:00 and %i:00" % (hour, (hour + 1)%24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

#https://pydeck.gl/
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
    "latitude": midpoint[0],
    "longitude": midpoint[1],
    "zoom": 11,#Initial camera angle relative to the map, defaults to a fully zoomed out 0
    },
    layers = [
    #https://deck.gl/docs/api-reference/aggregation-layers/hexagon-layer
       pdk.Layer(
       "HexagonLayer",#The Hexagon Layer renders a hexagon heatmap based on an array of points. It takes the radius of hexagon bin, projects points into hexagon bins. 
       data= data[['date/time', 'latitude', 'longitude']],
       get_position=['longitude', 'latitude'],
       radius=100, #Radius of hexagon bin in meters.(size of points in map)
       extruded=True, #3-d visulations
       elevation_range=[0, 1000], #for activate zoom in and zoom out
       ),
    ]
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour+1)))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute':range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected type")
select=st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrains':
    st.write(original_data.query("injured_pedstrains >=1")[["on_street_name", "injured_pedstrains"]].sort_values(by=['injured_pedstrains'], ascending=False).dropna(how='any')[:5])

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >=1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclistss'], ascending=False).dropna(how='any')[:5])

else:
    st.write(original_data.query("injured_motorists >=1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])

if st.checkbox("Show Raw Data", False):
	st.subheader('Raw Data')
	st.write(data)
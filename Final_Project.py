"""
CS 230 Final Program
Restaurant Data
Alexey Kolishchak
05/07/2022
The work is completed individually
"""

import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt
import math
import pandas as pd


MAP = "Map"
QUERY1 = "Restaurant Search"
QUERY2 = "Top Ten Restaurants by Name"
QUERY3 = "Top Ten Restaurants by State"
QUERY4 = "Top 5 States by Name"
QUERY5 = "Show Distances"


def map_display(data):
    """
    Displays map of all restaurants in the data
    :param data: DataFrame object
    :return: None
    """
    # initial view - coordinates of San Francisco, CA
    initial_view = pdk.ViewState(
        latitude=37.77,
        longitude=-122.4,
        zoom=11,
        pitch=30
    )
    layer = pdk.Layer(
        'HexagonLayer',
        data=data,
        get_position=['longitude', 'latitude'],
        radius=100,
        extruded=True
    )
    layer1 = pdk.Layer(
        'TextLayer',
        data=data,
        pickable=False,
        get_position=['longitude', 'latitude'],
        get_text='name',
        get_size=100,
        sizeUnits='meters',
        get_color=[0, 0, 0],
        get_angle=0,
        getTextAnchor= '"middle"',
        get_alignment_baseline='"bottom"'
    )
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=initial_view,
        layers=[layer, layer1]
    ))


def search(data):
    """
    Show address of specific restaurant selected via select boxes
    :param data: DataFrame object
    :return: none
    """
    states = sorted(data['province'].unique())
    state_select = st.selectbox("Select a state", states)
    cities = sorted(data.query('province == @state_select')['city'].unique())
    city_select = st.selectbox("Select a city", cities)
    networks = sorted(data.query('province == @state_select and city == @city_select')['name'].unique())
    network_select = st.selectbox("Select a restaurant network", networks)

    address_query = data.query(f'province == @state_select and city == @city_select and name == @network_select')['address']
    st.dataframe(address_query)


def top_ten_name(data):
    """
    Displays pie chart of top 10 most restaurants by Name
    :param data: DataFrame object
    :return: None
    """
    top_number = 10
    shares = data.groupby('name').size().sort_values(ascending=False).iloc[:top_number]
    fig, ax = plt.subplots()
    ax.pie(shares, labels=shares.keys(), autopct='%1.1f%%')
    st.pyplot(fig)


def top_ten_state(data):
    """
    Create a horizontal bar chart showing the top ten most common restaurants in the selected state
    :param data: DataFrame object
    :return: none
    """
    top_number = 10
    states = sorted(data['province'].unique())
    state_select = st.selectbox("Select a state", states)
    networks = data.query('province == @state_select')
    shares = networks.groupby('name').size().sort_values(ascending=False).iloc[:top_number]
    fig, ax = plt.subplots()
    ax.barh(width=shares, y=shares.keys())
    st.pyplot(fig)


def search_top_five_by_state(data):
    """
    Create a vertical bar chart showing the quantity and locations of the selected name of restaurant
    :param data: DataFrame object
    :return: none
    """
    top_number = 5
    networks = sorted(data['name'].unique())
    state_network = st.selectbox("Select a restaurant", networks)
    networks = data.query('name == @state_network')
    shares = networks.groupby('province').size().sort_values(ascending=False).iloc[:top_number]
    fig, ax = plt.subplots()
    ax.bar(height=shares, x=shares.keys())
    st.pyplot(fig)


def get_distance(longitude1, latitude1, longitude2, latitude2):
    """
    Calculating distance between earth coordinates
    :param longitude1: Longitude of point 1
    :param latitude1: Latitude of point 1
    :param longitude2: Longitude of point 2
    :param latitude2: Latitude of point 2
    :return: Distance: distance in miles
    """
    a = math.sin((latitude2 - latitude1) / 2)**2 + \
        math.cos(latitude1) * math.cos(latitude2) * math.sin((longitude2 - longitude1) / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = 3958.8 * c
    return distance


def show_distances(data):
    """
    Select a restaurant and show distances to all other in the same city
    :param data: DataFrame object
    :return:
    """
    states = sorted(data['province'].unique())
    state_select = st.selectbox("Select a state", states)
    cities = sorted(data.query('province == @state_select')['city'].unique())
    city_select = st.selectbox("Select a city", cities)
    networks = sorted(data.query(f'province == @state_select and city == @city_select')['name'].unique())
    network_select = st.selectbox("Select a restaurant network", networks)

    address_query = data.query(f'province == @state_select and city == @city_select and name == @network_select')
    address_select = st.selectbox("Select address", address_query['address'])

    selection = data.query(f'province == @state_select and city == @city_select and name == @network_select and address == @address_select')
    longitude1 = math.radians(selection['longitude'])
    latitude1 = math.radians(selection['latitude'])

    all_restaurants_in_city = data.query(f'province == @state_select and city == @city_select')
    longitude_list = [math.radians(x) for x in all_restaurants_in_city['longitude'].to_list()]
    latitude_list = [math.radians(x) for x in all_restaurants_in_city['latitude'].to_list()]

    distances = []
    for longitude2, latitude2 in zip(longitude_list, latitude_list):
        distance = get_distance(longitude1, latitude1, longitude2, latitude2)
        distances.append(distance)

    all_restaurants_in_city['distance'] = distances
    st.subheader('Distances from the selected restaurant to all restaurants in the same city, in miles')
    st.dataframe(all_restaurants_in_city[['name', 'address', 'distance']].sort_values(by=['distance']))


def main():
    """
    Main entry point
    :return: None
    """
    # read data
    data = pd.read_csv("Fast_Food_Restaurants_8000_sample.csv")
    # clean data
    data.dropna(how='any', inplace=True)
    data['name'] = data['name'].str.upper().str.replace('[^\w\s]', '')

    # streamlit controls
    radio_state = st.sidebar.radio("Please select a query:", (MAP, QUERY1, QUERY2, QUERY3, QUERY4, QUERY5))
    st.title('Fast Food Restaurants')
    st.header(radio_state)
    if radio_state == MAP:
        map_display(data)
    elif radio_state == QUERY1:
        search(data)
    elif radio_state == QUERY2:
        top_ten_name(data)
    elif radio_state == QUERY3:
        top_ten_state(data)
    elif radio_state == QUERY4:
        search_top_five_by_state(data)
    elif radio_state == QUERY5:
        show_distances(data)


# call entry point
main()









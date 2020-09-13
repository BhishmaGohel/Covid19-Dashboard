import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import seaborn as sns
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
import folium



st.title("Covid-19 pandamic")
st.markdown("This application is streamlit base website which use to do COVID_19 pandamic analysis using some datascience concepts 🦠🌎📊")

st.markdown("Note:")
st.markdown("This application is based on the US database as state wise and the other country wise")

input_s = st.text_input('Enter the date for the corona report in 01-01-2020 (MM-DD-YYYY) format')
sentence = input_s + ".csv"



if (input_s != ""):

    DATA_URL = (
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/" + sentence
    )

    if st.sidebar.checkbox("Show Github link for raw data", False):
        st.markdown("Link of raw database for analysis")
        st.markdown(DATA_URL)



    @st.cache(persist=True)
    def load_data(nrows):
        data = pd.read_csv(DATA_URL, nrows=nrows, sep=',')
        data.dropna(subset=['Lat', 'Long_'], inplace=True)
        lowercase = lambda x: str(x).lower()
        data.rename(lowercase, axis="columns", inplace=True)
        data.rename(columns={"long_": "lon"}, inplace=True)
        data.rename(columns={"last_update": "date/time"}, inplace=True)
        data.rename(columns={"case-fatality_ratio": "case_fatality_ratio"}, inplace=True)
        return data

    data = load_data(46137)

    if st.sidebar.checkbox("Show Raw Data", False):
        st.subheader('Raw Data')
        st.write(data)

    US_name = ['US']
    US_data_list = data['country_region'].isin(US_name)
    US_data = data[US_data_list]
    #st.write(US_data)

    st.markdown("Word Cloud on the basis of the positive cases in the US states")
    text = ""
    for i in US_data['province_state'].unique():
        text += "".join(i)+" "
    wordcloud = WordCloud(max_words=2000,collocations=False,background_color="white").generate(text)
    plt.figure(figsize=(15,15))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.figure(1,figsize=(15, 10))
    plt.show()
    st.pyplot()

    if st.checkbox("Click checkbox Visulization for all over the world", False):
	    if st.checkbox("Show confirm case fron all over the world", False):
	        fig = px.choropleth(data, locations="country_region", 
	                        locationmode='country names', color="confirmed", 
	                        hover_name="country_region", range_color=[1,7000], 
	                        color_continuous_scale="aggrnyl", 
	                        title='Countries with Confirmed Cases')
	        st.plotly_chart(fig)

	    if st.checkbox("Show deaths fron all over the world", False):
	        fig_1 = px.choropleth(data, locations="country_region", 
	                        locationmode='country names', color="deaths", 
	                        hover_name="country_region", range_color=[1,7000], 
	                        color_continuous_scale="aggrnyl", 
	                        title='Countries with Deaths')
	        st.plotly_chart(fig_1)

	        

	    if st.checkbox("Show recovered case fron all over the world", False):
	        fig_2 = px.choropleth(data, locations="country_region", 
	                        locationmode='country names', color="recovered", 
	                        hover_name="country_region", range_color=[1,7000], 
	                        color_continuous_scale="aggrnyl", 
	                        title='Countries with Recovered Cases')
	        st.plotly_chart(fig_2)
    

    st.header("Which data you want to visulize")
    select = st.selectbox('Affected class', ['Confirm Cases of COVID-19', 'Death by COVID-19', 'Recovery by COVID-19'])

    if select == 'Confirm Cases of COVID-19':
        st.header("Where are the most Cases occured in the world?")
        confirm_max = np.max(data['confirmed'])
        dead_people = st.slider("Number of Cases by COVID-19 virus", 0,int(confirm_max))
        st.map(data.query("confirmed >= @dead_people")[["lat", "lon"]].dropna(how="any"))
        #st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how="any")[:5])

    elif select == 'Death by COVID-19':
        st.header("Where are the most Death occure in the world?")
        dead_max = np.max(data['deaths'])
        dead_people = st.slider("Number of Death by COVID-19 virus", 0, int(dead_max))
        st.map(data.query("deaths >= @dead_people")[["lat", "lon"]].dropna(how="any"))
        #st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how="any")[:5])

    else:
        st.header("Where are the most Recovery occure in the world?")
        Recovery_max = np.max(data['recovered'])
        dead_people = st.slider("Number of Recovery by COVID-19 virus", 0, int(Recovery_max))
        st.map(data.query("recovered >= @dead_people")[["lat", "lon"]].dropna(how="any"))
        #st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how="any")[:5])





    st.title("State Vise analysis in United States Of America")
    PROVINCE_STATE = US_data['province_state'].unique()
    PROVINCE_STATE_SELECTED = st.multiselect('Select State from the list', PROVINCE_STATE)

    if(PROVINCE_STATE_SELECTED != []):
        mask_state = data['province_state'].isin(PROVINCE_STATE_SELECTED)
        

        for i in PROVINCE_STATE_SELECTED:
            s = [i]
            mask_state = data['province_state'].isin(s)
            data_for_state_wise = data[mask_state]
            #st.write(data_for_state_wise)
            data_for_state_wise.rename(columns={"lat": "latitude"}, inplace=True)
            data_for_state_wise.rename(columns={"lon": "longitude"}, inplace=True)


            midpoint = (np.average(data_for_state_wise["latitude"]), np.average(data_for_state_wise["longitude"]))
            st.write(pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state={
                    "latitude": midpoint[0],
                    "longitude": midpoint[1],
                    "zoom": 11,
                    "pitch": 50,
                },
                layers=[
                    pdk.Layer(
                    "HexagonLayer",
                    data=data_for_state_wise[['latitude', 'longitude']],
                    get_position=["longitude", "latitude"],
                    auto_highlight=True,
                    radius=2000,
                    extruded=True,
                    pickable=True,
                    elevation_scale=4,
                    elevation_range=[0, 200000],
                    ),
                ],
            ))

            


            #m = folium.Map(location=[20, 0], title="Map for Recovery")
            
            #df_data_for_state_wise = pd.DataFrame(data_for_state_wise)

            #for i in range(0,len(data_for_state_wise)):
            #    st.markdown(df_data_for_state_wise.iloc[i]['longitude'], df_data_for_state_wise.iloc['latitude'])
            #    folium.Circle(
            #        location = [data_for_state_wise[i]['lon'], data_for_state_wise[i]['lat']],
            #        popup = data_for_state_wise[i]['admin2'],
            #        radius = data_for_state_wise['deaths']*100,
            #        color = 'crimson',
            #        fill = True,
            #        fill_color = 'crimson'
            #      ).add_to(m)
                    

            #st.markdown(m)
            
            average_no_of_positive_case_US = US_data['confirmed'].mean()
            average_no_of_positive_case_state_wise = data_for_state_wise['confirmed'].mean()

            average_no_of_death_US = US_data['deaths'].mean()
            average_no_of_death_state_wise = data_for_state_wise['deaths'].mean()

            average_no_of_recovered_case_US = US_data['recovered'].mean()
            average_no_of_recovered_case_state_wise = data_for_state_wise['recovered'].mean()

            average_no_of_incidence_rate_US = US_data['incidence_rate'].mean()
            average_no_of_incidence_rate_state_wise = data_for_state_wise['incidence_rate'].mean()

            average_no_of_case_fatality_ratio_US = US_data['case_fatality_ratio'].mean()
            average_no_of_case_fatality_ratio_state_wise = data_for_state_wise['case_fatality_ratio'].mean()

            st.markdown("Here the comparision for state %s as (State/US)"% (i))
            st.markdown(" Positive Case : %i / %i " %( average_no_of_positive_case_state_wise, average_no_of_positive_case_US))
            st.markdown(" Deaths : %i / %i " %(average_no_of_death_state_wise,average_no_of_death_US))
            st.markdown(" Recovered Case : %i / %i " %(average_no_of_recovered_case_state_wise,average_no_of_recovered_case_US))
            st.markdown(" Incidence Rate : %i / %i " %(average_no_of_incidence_rate_state_wise,average_no_of_incidence_rate_US))
            st.markdown(" case fatality ratio : %i / %i " %(average_no_of_case_fatality_ratio_state_wise,average_no_of_case_fatality_ratio_US))

            if st.checkbox("Show Raw Data for state %s" %(i)):
                st.subheader('Raw Data')
                st.write(data_for_state_wise)

    

add_selectbox = st.sidebar.selectbox(
    'Contact ME!',
    ( 'LinkedIn', 'Github', 'Email')
    )
        
if(add_selectbox == 'Email'):
        st.markdown("Gmail:")
        st.markdown("bhishmagohel09@gmail.com")
elif(add_selectbox == 'LinkedIn'):
        st.markdown("LinkedIn:")
        st.markdown("https://www.linkedin.com/in/bhishma-gohel-754297155/")
elif(add_selectbox == 'Github'):
        st.markdown("Github:")
        st.markdown("https://github.com/BishmaGohel")    
    

    
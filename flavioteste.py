#import geopandas
from datetime import datetime

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

st.set_page_config(layout='wide' )

@st.cache( allow_output_mutation='True' )
def get_data ( path ):
    data = pd.read_csv( path )

    return data

@st.cache( allow_output_mutation='True')
#def get_geofile( url ):
#    geofile = geopandas.read_file( url )

##    return geofile

def set_feature( data ):
    # add new features
    data['price_m2'] = data['price'] / data['sqft_lot']
    return data

def overview_data( data ):
    f_attributes = st.sidebar.multiselect('Entre com as colunas', data.columns)
    f_zipcode = st.sidebar.multiselect(
            'Entre com os Ceps',
            data['zipcode'].unique()    )
    st.title('Visão dos Dados')
    if ( f_zipcode != []) & ( f_attributes != []):
        data = data.loc[data['zipcode'].isin( f_zipcode), f_attributes]
    elif ( f_zipcode != []) & ( f_attributes == []):
        data = data.loc[data['zipcode'].isin( f_zipcode), :]
    elif (f_zipcode == []) & (f_attributes != []):
        data = data.loc[:, f_attributes]
    else:
        data = data.copy()

    st.dataframe( data.head())

    c1,c2 = st.beta_columns((1, 1) )

    df1 = data[['id', 'zipcode']].groupby('zipcode' ).count().reset_index()
    df2 = data[['price', 'zipcode']].groupby('zipcode' ).mean().reset_index()
    df3 = data[['sqft_living', 'zipcode']].groupby('zipcode' ).mean().reset_index()
    df4 = data[['price_m2', 'zipcode']].groupby('zipcode' ).mean().reset_index()

    m1 = pd.merge( df1, df2, on='zipcode', how='inner')
    m2 = pd.merge( m1, df3, on='zipcode', how='inner')
    df = pd.merge( m2, df4, on='zipcode', how='inner')

    df.columns = ['ZIPCODE', 'TOTAL HOUSES', 'PRICE', 'SQRT LIVING',
                  'PRICE/M2']

    c1.header( 'Average Values')
    c1.dataframe( df, height=600)

    num_attributes = data.select_dtypes( include = ['int64','float64'])
    media = pd.DataFrame(num_attributes.apply( np.mean ) )
    mediana = pd.DataFrame (num_attributes.apply ( np.median ) )
    std = pd.DataFrame (num_attributes.apply ( np.std ) )

    max_ = pd.DataFrame (num_attributes.apply ( np.max ) )
    min_ = pd.DataFrame (num_attributes.apply ( np.min ) )

    df1 = pd.concat([max_, min_, media, mediana, std], axis=1 ).reset_index()

    df1.columns = ['atributes', 'max', 'min', 'mean', 'median', 'std']

    c2.header( 'Descriptive Analysis')
    c2.dataframe ( df1, height=800 )

    return None

def portfolio_density( data ):
    st.title( 'Region Overview')

    c1,c2 = st.beta_columns(( 1, 1 ))
    c1.header( 'Portifolio Density' )

    df = data.sample( 10 )

    density_map = folium.Map( location=[data['lat'].mean(),
                              data['long'].mean() ],
                              default_zoom_start=15)

    marker_cluster = MarkerCluster().add_to( density_map)
    for name, row in df.iterrows():
        folium.Marker( [row['lat'], row['long'] ],
             popup= 'Sold r$ {0} on: {1}. Features : {2} sqft, {3} beddrooms, {4} bathrooms, year ' \
                    'bulit: {5}'.format(
                    row['price'],
                    row['date'],
                    row['sqft_living'],
                    row['bedrooms'],
                    row['bathrooms'],
                    row['yr_built'] ) ).add_to( marker_cluster )

    with c1:
        folium_static( density_map)

    return None
"""
    c2.header( 'Price Density')

    df = data[['price', 'zipcode']].groupby( 'zipcode').mean().reset_index()
   df.columns = ['ZIP','PRICE']

    geofile = geofile[geofile['ZIP'].isin( df['ZIP'].tolist() )]
    region_price_map = folium.Map( location=[data['lat'].mean(),
                              data['long'].mean() ],
                              default_zoom_start=15)

    region_price_map.cloropleth( data = df,
                                 geo_data = geofile,
                                 columns=['ZIP','PRICE'],
                                 key_on='feature.properties.ZIP',
                                 fill_color='YlOrRd',
                                 fill_opacity = 0.7,
                                 line_opacity = 0.2,
                                 legend_name= 'AVG PRICE' )

    with c2:
        folium_static( region_price_map)
"""


def commercial_distribution ( data ):
    st.sidebar.title( 'Comercial Options')
    st.title(' Comercial Attributes')

    data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')
    min_year_built = int( data['yr_built'].min())
    max_year_built = int(data['yr_built'].max())
    st.sidebar.subheader('Select max year')
    f_year_built = st.sidebar.slider('Year Built', min_year_built,
                                     max_year_built,
                                     min_year_built)

    st.header('Average price per year built')
    df = data.loc[data['yr_built'] < f_year_built]
    df = df[['yr_built', 'price']].groupby('yr_built').mean().reset_index()

    fig = px.line(df, x='yr_built', y='price')
    st.plotly_chart( fig, use_container_width=True)
    #=================================================
    st.header('Average price day')
    st.sidebar.subheader('Select max Date')
    # filtros
    min_date = datetime.strptime( data['date'].min(), '%Y-%m-%d' )
    max_date = datetime.strptime( data['date'].max(), '%Y-%m-%d' )

    f_date = st.sidebar.slider('Date', min_date, max_date, min_date)

    #data filtros
    data['date'] = pd.to_datetime( data['date'])
    df = data.loc[data['date'] < f_date]
    df = df[['date', 'price']].groupby('date').mean().reset_index()
    # plotagem
    fig = px.line( df, x='date', y='price')
    st.plotly_chart( fig, use_container_width=True)

    # histograma
    st.header('price distribuição')
    st.sidebar.subheader('select max price')

    # filtro
    min_price = int( data['price'].min())
    max_price = int( data['price'].max())
    avg_price = int( data['price'].mean())

    #data_filtering
    f_price = st.sidebar.slider('price', min_price, max_price, min_price)
    df = data.loc[data['price'] < f_price]

    #data plotagem
    fig = px.histogram( df, x='price', nbins=50)
    st.plotly_chart( fig, use_container_width=True)

    return None




def attributes_distribution ( data ):

    st.sidebar.title( 'Attributes Options')
    st.title(' House Attributes')
    #filtros
    f_bedrooms = st.sidebar.selectbox( 'Max number of bedrooms',
                                       sorted( set( data['bathrooms'].unique() )))
    f_bathrooms = st.sidebar.selectbox( 'Max number of bathrooms',
                                        sorted( set( data['bathrooms'].unique() )))

    c1, c2 = st.beta_columns( 2 )

    # houses per bedrooms
    c1.header('Houses per Bedrooms')
    df = data.loc[data['bedrooms'] < f_bedrooms]
    fig = px.histogram( df, x='bedrooms', nbins=19)
    c1.plotly_chart( fig, use_container_width=True)

    # houses per bathrooms
    c2.header('Houses per bathrooms')
    df = data.loc[data['bathrooms'] < f_bathrooms]
    fig = px.histogram( data, x='bathrooms', nbins=19)
    c2.plotly_chart( fig, use_container_width=True)

    #filtros
    f_floors = st.sidebar.selectbox('Max numbers of floors',
                                    sorted( set( data['floors'].unique() )))
    f_water_view = st.sidebar.checkbox( 'Only Houses with Water View')

    c1, c2 = st.beta_columns( 2 )

    #house per floors
    c1.header('house per floors')
    df = data[data['floors'] < f_floors]
    #plot
    fig = px.histogram( df, x='floors', nbins=19)
    c1.plotly_chart( fig, use_container_width=True)

    #house per water view
    if f_water_view:
        df = data[data['waterfront'] == 1]
    else:
        df = data.copy()

    fig = px.histogram( df, x='waterfront', nbins=10)
    c2.plotly_chart( fig, use_container_width=True)

    return None
if __name__ == '__main__':

    path = 'kc_house_data.csv'
    url = 'https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'
    data = get_data( path )
#    geofile = get_geofile( url )
    data = set_feature( data )
    overview_data( data )

#    portfolio_density( data, geofile )
    portfolio_density(data)
    commercial_distribution ( data )

    attributes_distribution ( data )

#data = pd.read_excel('dados/DadosBO_2020_1fc.xls')
#st.title('Teste de mapas com leitura direta')
#st.write(data.head())
#st.write(np.shape(data))


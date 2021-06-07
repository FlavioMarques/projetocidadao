import os
import random
import urllib

# import swifter as swf
import folium
import mysql.connector
import pandas as pd
import plotly.express as px
import streamlit as st
from folium.plugins import MarkerCluster
from mysql.connector import Error
from streamlit_echarts import st_echarts
from streamlit_folium import folium_static

#===========================================================================================

st.set_page_config(layout='wide')

#   dados de conexão ao banco de dados
onde = '127.0.0.1'
banco = '5sec'
usuario = 'root'
senha = 'amanda05'
cursor = ''
#===========================================================================================

# Streamlit encourages well-structured code, like starting execution in a main() function.
def main():
    # Render the readme as markdown using st.markdown.
    readme_text = st.markdown(get_file_content_as_string("instructions.md"))

    # Download external dependencies.
    for filename in EXTERNAL_DEPENDENCIES.keys():
        download_file(filename)

    # Once we have the dependencies, add a selector for the app mode on the sidebar.
    st.sidebar.title("O que vamos fazer...")
    app_mode = st.sidebar.selectbox("Escolha o modo do aplicativo: ",
        ["Mostrar Instruções", "Executar o Aplicativo", "Show the source code"])
    if app_mode == "Mostrar Instruções":
        st.sidebar.success('Para continuar, selecione "Executar o aplicativo".".')
    elif app_mode == "Show the source code":
        readme_text.empty()
        st.code(get_file_content_as_string(".testsql.py"))
    elif app_mode == "Executar o Aplicativo":
        readme_text.empty()
        run_the_app()
#===========================================================================================

def run_the_app():
    # To make Streamlit fast, st.cache allows us to reuse computation across runs.
    # In this common pattern, we download data from an endpoint only once.

    #conectando ao MySql
    conMySQL = conectar(onde, banco, usuario, senha)

    #Lista de municipios dos dados
    municipios = busca_cidades(conMySQL)

    #Menu de escolha do municipio a ser verificado
    st.sidebar.header('Filtragem dos Dados da SSP')

    f_cidade = st.sidebar.selectbox('Escolha o Municipio :', municipios)

    if f_cidade:
        #leitura dos dados do municipio selecionado

        dadosbrutos = busca_dadosbrutos(f_cidade, conMySQL)
        dadoscomlogr = busca_dadoscomlogr(f_cidade, conMySQL)
        dados = busca_dadoslimpos(f_cidade, conMySQL)

        f_area = st.sidebar.selectbox('Escolha a area do fato:', sorted( set(filter(None, dados['SECCIONAL'].unique()))))

        f_veiculos = st.sidebar.selectbox('Escolha os veiculos:', sorted( set(filter(None, dados['DESCR_MARCA_VEICULO'].unique()))))

        f_fatos = st.sidebar.selectbox('Escolha os fatos:', sorted( set(filter(None, dados['RUBRICA'].unique()))))

        df_data = pd.to_datetime(dados['DATAOCORRENCIA']).dt.date.drop_duplicates()

        min_date = min(df_data)
        max_date = max(df_data)
        print(min_date)
        print(max_date)
#        f_date = st.sidebar.slider('DATA:', min_date, max_date, min_date)
        # data filtros
        print(df_data)
        print('zzzzzzz')
        df_data = pd.to_datetime(dados['DATAOCORRENCIA'])
        print(df_data)
        print('kkkkkkkkkkkkkkkk')
#        df = df_data[['DATAOCORRENCIA']] < f_date
#       df = df_data[['DATAOCORRENCIA', 'RUBRICA']].groupby('DATAOCORRENCIA').mean().reset_index()
        # plotagem
#       st.line_chart(df)
#       fig = px.line(df, x='date', y='price')
#       st.plotly_chart(fig, use_container_width=True)

        f_morte = st.sidebar.checkbox('Casos com morte ?',)
        f_recuperados = st.sidebar.checkbox('Veiculos recuperados ?',)
        f_carga = st.sidebar.checkbox('Casos de Carga ?',)
        f_receptados = st.sidebar.checkbox('Local de Receptação ?',)
    else:
        dados = []

    #Tela de trabalho/analise
    st.title('Escolha o Municipio que deseja analisar sobre Furto/Roubo de Veiculos, baseado no endereço/data do fato: ')
    if len(dados) > 0:
        analise1 = 'Qtde de dados limpos (logradouros geocofificados e data coerentes): ' + str(len(dados)) + ' ==> ' + f_cidade + ' simples amostra em 5 linhas...'
        analise2 = 'Dados lidos com logradouros geocodificados e/ou fora da data(fora do escopo): ' + str(dadoscomlogr[0])
        analise3 = 'Dados brutos lidos, com logradouros vazios, e/ou fora da data (fora do escopo): ' + str(dadosbrutos[0])

        st.text(analise3)
        st.text(analise2)
        st.text(analise1)

        st.dataframe(dados.head().style.highlight_max(axis=0))

        data = pd.DataFrame(columns=('Data', 'Qt_BOs'))

        data['Data'] = dados['DATAOCORRENCIA']
        data['Qt_BOs'] = dados['NUMERO_BOLETIM']
        data['Data'] = pd.to_datetime(data['Data'])
        df = data[['Data', 'Qt_BOs']].groupby('Data').count().reset_index()
        dfx = df['Qt_BOs']
        media = (dfx).mean()
        maximo = (dfx).max()
        print(media)
        # plotagem

        c1, c2 = st.beta_columns( 2 )
        c1.header('Casos por dia :')
        fig = px.line(df, x='Data', y='Qt_BOs')
        c1.plotly_chart(fig, use_container_width=False)

        c2.header('Roubos/Furtos :')
        datak = pd.DataFrame(columns=('Fato', 'Qt_BOs'))
        datak['Fato'] = dados['BASESSP']
        datak['Qt_BOs'] = dados['NUMERO_BOLETIM']
        dfw = datak[['Fato', 'Qt_BOs']].groupby('Fato').count().reset_index()
        fig = px.histogram(dfw, x='Fato', y='Qt_BOs', nbins=10)
        c2.plotly_chart(fig, use_container_width=True)


        st.header('Detalhes do Furto/Roubo pela RUBRICA:')
        datak = pd.DataFrame(columns=('Fato', 'Qt_BOs'))
        datak['Fato'] = dados['RUBRICA']
        datak['Qt_BOs'] = dados['NUMERO_BOLETIM']
        dfw = datak[['Fato', 'Qt_BOs']].groupby('Fato').count().reset_index()
        fig = px.histogram(dfw, x='Fato', y='Qt_BOs', nbins=10)
        st.plotly_chart(fig, use_container_width=True)

        st.header('Detalhes do Furto/Roubo pelo modelo base:')
        datak = pd.DataFrame(columns=('Veiculo', 'Qt_BOs'))
        datak['Veiculo'] = dados['MODELO_BASE']
        datak['Qt_BOs'] = dados['NUMERO_BOLETIM']
        dfw = datak[['Veiculo', 'Qt_BOs']].groupby('Veiculo').count().reset_index()
        fig = px.histogram(dfw, x='Veiculo', y='Qt_BOs', nbins=10)
        st.plotly_chart(fig, use_container_width=True)

        option = {
                "tooltip": {"position": "top"},
                "visualMap": {
                    "min": 0,
                    "max": maximo,
#                    "calculable": True,
                    "type": 'piecewise',
                    "orient": "horizontal",
                    "left": "center",
                    "top": "top",
                },
                "calendar": [
                    {"range": "2020", "cellSize": ["auto", 20]},
                    {"top": 260, "range": "2021", "cellSize": ["auto", 20]},
                ],
                "series": [
                    {
                        "type": "heatmap",
                        "coordinateSystem": "calendar",
                        "calendarIndex": 0,
                        "data": get_virtual_data(df),
                    },
                ],
            }
        st_echarts(option, height="640px", key="echarts")

    if f_cidade:
        opcao = st.sidebar.checkbox('Mostrar Mapa ?')
    else:
        opcao = False

    if opcao:
        mapa(dados, f_cidade)

    st.balloons()
    desconectar(conMySQL)
    return
#===========================================================================================
def get_virtual_data(df):
    df['Data'] = df['Data'].apply(str)
    h = df.values.tolist()
    return h

#===========================================================================================

#@st.cache( allow_output_mutation='True' )
def conectar(onde, banco, usuario, senha):
    try:
        conMySQL = mysql.connector.connect(host=onde, database=banco, user=usuario, password=senha)
    except Error as e:
        st.write("Erro ao acessar tabela MySQL", e)
    return conMySQL
#===========================================================================================

def desconectar(conMySQL):
    try:
        None
    except Error as e:
        st.write("Erro ao acessar tabela MySQL", e)
    finally:
        if (conMySQL.is_connected()):
            conMySQL.close()
            #            cursor.close()
            st.write("Conexão ao MySQL encerrada")
    return
#===========================================================================================

#@st.cache(hash_funcs={Connection: id})
def busca_cidades(conMySQL):
    try:
        consulta_sql = "select cidade as Munic from cidades order by cidade asc"
        cursor = conMySQL.cursor()
        cursor.execute(consulta_sql)
        resultado = cursor.fetchall()
        municipios = [res[0] for res in resultado]

    except Error as e:
        st.write("Erro ao acessar tabela MySQL", e)
    return municipios
#===========================================================================================
#@st.cache(hash_funcs={mysql.connector: id})
def busca_dadosbrutos(f_cidade, conMySQL):
    try:
        consulta_sql = "SELECT count(*) as total FROM 5sec.veic_ro_fu_2020 where CIDADE = %s "
        cursor = conMySQL.cursor()
        cursor.execute(consulta_sql, (f_cidade,))
        resultado = cursor.fetchall()

#        dfz = pd.read_sql(consulta_sql, conMySQL, params=(f_cidade,))
        dadosbrutos = resultado

    except Error as e:
        st.write("Erro ao acessar tabela MySQL", e)
    return dadosbrutos
#===========================================================================================

#@st.cache(hash_funcs={mysql.connector: id})
def busca_dadoscomlogr(f_cidade, conMySQL):
    try:
        consulta_sql = "SELECT count(*) as total FROM 5sec.veic_ro_fu_2020 where CIDADE = %s and latitude is not null"
        cursor = conMySQL.cursor()
        cursor.execute(consulta_sql, (f_cidade,))
        resultado = cursor.fetchall()
        print(resultado)
#        dfz = pd.read_sql(consulta_sql, conMySQL, params=(f_cidade,))
        dadoscomlogr = resultado
    except Error as e:
        st.write("Erro ao acessar tabela MySQL", e)
    return dadoscomlogr

#===========================================================================================
#@st.cache(hash_funcs={mysql.connector: id})
def busca_dadoslimpos(f_cidade, conMySQL):
    try:
        consulta_sql = "SELECT * FROM 5sec.veic_ro_fu_2020 where CIDADE = %s and latitude is not null and substring(dataocorrencia,7,4) >= 2019"
        dfz = pd.read_sql(consulta_sql, conMySQL, params=(f_cidade,))
        dadoslimpos = dfz
    except Error as e:
        st.write("Erro ao acessar tabela MySQL", e)
    return dadoslimpos

#===========================================================================================

@st.cache(show_spinner=False, suppress_st_warning=True)
def mapa(nx, f_cidade):
    st.title('Vista do Municipio Selecionado:')
    data = nx
    c1, c2, c3 = st.beta_columns((6, 1, 1))
    c1.header('Densidade por Local')

    df = data

    density_map = folium.Map(location=[data[['LATITUDE']].mean(),
                                       data[['LONGITUDE']].mean()],
                             default_zoom_start=15)

    marker_cluster = MarkerCluster().add_to(density_map)

    for name, row in df.iterrows():
        folium.Marker([row['LATITUDE'], row['LONGITUDE']],
                      popup='<b>Fatos : <p> {0} <p>  {1}  {2} <p> {3} , {4} - {5}<b>'.format(row['RUBRICA'],
                      row['DATAOCORRENCIA'], row['DESCR_MARCA_VEICULO'], row['LOGRADOURO'], row['NUMERO'],
                      row['CIDADE'])).add_to(marker_cluster)

    with c1:
        folium_static(density_map, width=1200, height=800)

    return None
#===========================================================================================

@st.cache(show_spinner=False)
def get_file_content_as_string(path):
    url = 'http://127.0.0.1/dashboard/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")
#===========================================================================================

# This file downloader demonstrates Streamlit animation.
def download_file(file_path):
    # Don't download the file twice. (If possible, verify the download using the file length.)
    if os.path.exists(file_path):
        if "size" not in EXTERNAL_DEPENDENCIES[file_path]:
            return
        elif os.path.getsize(file_path) == EXTERNAL_DEPENDENCIES[file_path]["size"]:
            return

    # These are handles to two visual elements to animate.
    weights_warning, progress_bar = None, None
    try:
        weights_warning = st.warning("Downloading %s..." % file_path)
        progress_bar = st.progress(0)
        with open(file_path, "wb") as output_file:
            with urllib.request.urlopen(EXTERNAL_DEPENDENCIES[file_path]["url"]) as response:
                length = int(response.info()["Content-Length"])
                counter = 0.0
                MEGABYTES = 2.0 ** 20.0
                while True:
                    data = response.read(8192)
                    if not data:
                        break
                    counter += len(data)
                    output_file.write(data)

                    # We perform animation by overwriting the elements.
                    weights_warning.warning("Downloading %s... (%6.2f/%6.2f MB)" %
                        (file_path, counter / MEGABYTES, length / MEGABYTES))
                    progress_bar.progress(min(counter / length, 1.0))

    # Finally, we remove these visual elements by calling .empty().
    finally:
        if weights_warning is not None:
            weights_warning.empty()
        if progress_bar is not None:
            progress_bar.empty()
#===========================================================================================

# This is the main app app itself, which appears when the user selects "Run the app".
# This is the main app app itself, which appears when the user selects "Run the app".

# Path to the Streamlit public S3 bucket
DATA_URL_ROOT = "https://streamlit-self-driving.s3-us-west-2.amazonaws.com/"

# External files to download.
EXTERNAL_DEPENDENCIES = {
    "yolov3.weights": {
        "url": "https://pjreddie.com/media/files/yolov3.weights",
        "size": 248007048
    },
    "yolov3.cfg": {
        "url": "https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg",
        "size": 8342
    }
}
#===========================================================================================

if __name__ == '__main__':

    main()
#===========================================================================================

#    path = 'kc_house_data.csv'
#    url = 'https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'
#    data = get_data( path )
#    geofile = get_geofile( url )
#    data = set_feature( data )
#    overview_data( data )
#    portfolio_density( data, geofile )
#    portfolio_density(data)
#    commercial_distribution ( data )
#    attributes_distribution ( data )

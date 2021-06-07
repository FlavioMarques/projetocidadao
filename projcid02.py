import os
import urllib
# import swifter as swf
from pathlib import Path
import folium
import mysql.connector
import pandas as pd
import plotly.express as px
import streamlit as st
from folium.plugins import MarkerCluster
from mysql.connector import Error
from streamlit_echarts import st_echarts
from streamlit_folium import folium_static
import time
import streamlit.components.v1 as components

import altair as alt
#import vegas_dataset

from pprint import pformat

# ===========================================================================================
st.set_page_config(layout='wide')

#   dados de conexão ao banco de dados
onde = '127.0.0.1'
banco = '5sec'
usuario = 'root'
senha = 'amanda05'
cursor = ''

#   Texto de introdução
introducao = """# *FMA - Consulting, data analysis, data science, public security --> Projeto Cidadão 2021*
# Projeto Cidadão 2021

## Maior qualidade de vida, em se tratando de Segurança Pública e Sociedade.

Facilitando ao Cidadão meios para fiscalizar e acompanhar no *tempo e no
espaço*, os locais onde reside, trabalha, estuda, pratica lazer...
considerando a segurança e o estado social deste lugares....
Através de dados públicos e das informações fornecidas pelo próprio Cidadão.

## *Fase 1*
Análise das informações públicas da [SSP - Secretaria de Segurança Pública de São Paulo.](http://www.ssp.sp.gov.br/transparenciassp/)

👈 ****Selecione _Executar o aplicativo_ na barra lateral para iniciar.****

Os dados estão em forma bruta, conforme foram baixados do site, nossa visão será baseada no endereço registrado no Boletim de Ocorrência, com base na cidade onde aconteceu o fato.
Faremos uma análise dos fatos, dentro de uma visão de **_Tempo/Espaço_**.

## Boa navegação, obrigado!!


### Questões? Comentários?

Por favor, utilize este email: marques.alexandre@gmail.com

 [Flavio Marques Alexandre Neto](mailto:marques.alexandre@gmail.com)
"""


# ===========================================================================================
# Streamlit encourages well-structured code, like starting execution in a main() function.
def main():
    # Render the readme as markdown using st.markdown.
    #intro_markdown = read_markdown_file("instructions.md")
    #readme_text = st.markdown(intro_markdown, unsafe_allow_html=True)

    readme_text = st.markdown(introducao)
    # Download external dependencies.

    # Once we have the dependencies, add a selector for the app mode on the sidebar.

    st.sidebar.title("O que vamos fazer...")

    app_mode = st.sidebar.selectbox("Escolha o modo do aplicativo: ",
                                    ["Mostrar Introdução", "Executar o Aplicativo" ])
    if app_mode == "Mostrar Introdução":
            st.sidebar.success('Para continuar, selecione "Executar o aplicativo".')
#    elif app_mode == "Show the source code":
#        readme_text.empty()
#        st.code(get_file_content_as_string("projcid02.py"))
    elif app_mode == "Executar o Aplicativo":
            readme_text.empty()
            run_the_app()

# ===========================================================================================

def run_the_app():
    # To make Streamlit fast, st.cache allows us to reuse computation across runs.
    # In this common pattern, we download data from an endpoint only once.
    startTime = time.time()
    # conectando ao MySql
    conMySQL = conectar(onde, banco, usuario, senha)

    # Lista de municipios dos dados
    municipios = busca_cidades(conMySQL)

    # Menu de escolha do municipio a ser verificado
    st.sidebar.header('Filtragem dos Dados da SSP')

    f_cidade = st.sidebar.selectbox('Escolha o Municipio :', municipios)

    if f_cidade:
        # leitura dos dados do municipio selecionado

        dadosbrutos = busca_dadosbrutos(f_cidade, conMySQL)
        dadoscomlogr = busca_dadoscomlogr(f_cidade, conMySQL)
        dados = busca_dadoslimpos(f_cidade, conMySQL)

        f_area = st.sidebar.selectbox('Escolha a area do fato:', sorted(set(filter(None, dados['SECCIONAL'].unique()))))

        f_veiculos = st.sidebar.selectbox('Escolha os veiculos:', sorted(set(filter(None, dados['MODELO_BASE'].unique()))))

        f_fatos = st.sidebar.selectbox('Escolha os fatos:', sorted(set(filter(None, dados['RUBRICA'].unique()))))


#=============================
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

        f_morte = st.sidebar.checkbox('Casos com morte ?', )
        f_recuperados = st.sidebar.checkbox('Veiculos recuperados ?', )
        f_carga = st.sidebar.checkbox('Casos de Carga ?', )
        f_receptados = st.sidebar.checkbox('Local de Receptação ?', )
    else:
        dados = []

    # Tela de trabalho/analise
    st.title(
        'Escolha o Municipio que deseja analisar sobre Furto/Roubo de Veiculos, baseado no endereço/data do fato: ')
    if len(dados) > 0:
        analise1 = 'Qtde de dados limpos (logradouros geocofificados e data coerentes): ' + str(
            len(dados)) + ' ==> ' + f_cidade + ' simples amostra em 5 linhas...'
        analise2 = 'Dados lidos com logradouros geocodificados e/ou fora da data(fora do escopo): ' + str(
            dadoscomlogr[0])
        analise3 = 'Dados brutos lidos, com logradouros vazios, e/ou fora da data (fora do escopo): ' + str(
            dadosbrutos[0])

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

        #c1, c2 = st.beta_columns(2)
        st.header('Casos por dia :')
        fig = px.line(df, x='Data', y='Qt_BOs')
        st.plotly_chart(fig, use_container_width=True)

        st.header('Casos distribuidos por dia da semana :')
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
        st_echarts(option, height="400px", key="echarts")

        st.header('Roubos/Furtos/Recuperação Veiculos:')
        datak = pd.DataFrame(columns=('Fato', 'Qt_BOs'))
        datak['Fato'] = dados['BASESSP']
        datak['Qt_BOs'] = dados['NUMERO_BOLETIM']
        dfw = datak[['Fato', 'Qt_BOs']].groupby('Fato').count().reset_index()
        fig = px.histogram(dfw, x='Fato' , y='Qt_BOs', nbins=10)
        st.plotly_chart(fig, use_container_width=True)

        st.header('Crimes associados ao Furto/Roubo de veiculos:')
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
        dfw.sort_values(by=['Qt_BOs'], inplace=True, ascending=False)

        fig = px.histogram(dfw, x='Veiculo', y='Qt_BOs', nbins=10)
        st.plotly_chart(fig, use_container_width=True)


    if f_cidade:
        opcao = st.sidebar.checkbox('Mostrar Mapa ?')
    else:
        opcao = False

    if opcao:
        mapa(dados, f_cidade)

    st.balloons()
    desconectar(conMySQL)
    executionTime = (time.time() - startTime)
    st.write('Tempo de execução em segundos : ' + str(executionTime))
    return


# ===========================================================================================
def get_virtual_data(df):
    df['Data'] = df['Data'].apply(str)
    h = df.values.tolist()
    return h

# ===========================================================================================
def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()


# ===========================================================================================

# @st.cache( allow_output_mutation='True' )
def conectar(onde, banco, usuario, senha):
    try:
        conMySQL = mysql.connector.connect(host=onde, database=banco, user=usuario, password=senha)
    except Error as e:
        st.write("Erro ao acessar tabela MySQL", e)
    return conMySQL


# ===========================================================================================

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


# ===========================================================================================

# @st.cache(hash_funcs={Connection: id})
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


# ===========================================================================================
# @st.cache(hash_funcs={mysql.connector: id})
def busca_dadosbrutos(f_cidade, conMySQL):
    try:
        consulta_sql = "SELECT count(ID) as total FROM 5sec.veic_ro_fu_2020 where CIDADE = %s "
        cursor = conMySQL.cursor()
        cursor.execute(consulta_sql, (f_cidade,))
        resultado = cursor.fetchall()

        #        dfz = pd.read_sql(consulta_sql, conMySQL, params=(f_cidade,))
        dadosbrutos = resultado

    except Error as e:
        st.write("Erro ao acessar tabela MySQL", e)
    return dadosbrutos


# ===========================================================================================

# @st.cache(hash_funcs={mysql.connector: id})
def busca_dadoscomlogr(f_cidade, conMySQL):
    try:
        consulta_sql = "SELECT count(ID) as total FROM 5sec.veic_ro_fu_2020 where CIDADE = %s and latitude is not null"
        cursor = conMySQL.cursor()
        cursor.execute(consulta_sql, (f_cidade,))
        resultado = cursor.fetchall()
        print(resultado)
        #        dfz = pd.read_sql(consulta_sql, conMySQL, params=(f_cidade,))
        dadoscomlogr = resultado
    except Error as e:
        st.write("Erro ao acessar tabela MySQL", e)
    return dadoscomlogr


# ===========================================================================================
# @st.cache(hash_funcs={mysql.connector: id})
def busca_dadoslimpos(f_cidade, conMySQL):
    try:
        consulta_sql = "SELECT * FROM 5sec.veic_ro_fu_2020 where CIDADE = %s and latitude is not null and substring(dataocorrencia,7,4) >= 2020"
        dfz = pd.read_sql(consulta_sql, conMySQL, params=(f_cidade,))
        dadoslimpos = dfz
    except Error as e:
        st.write("Erro ao acessar tabela MySQL", e)
    return dadoslimpos


# ===========================================================================================

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
                                                                                             row['DATAOCORRENCIA'],
                                                                                             row['DESCR_MARCA_VEICULO'],
                                                                                             row['LOGRADOURO'],
                                                                                             row['NUMERO'],
                                                                                             row['CIDADE'])).add_to(
            marker_cluster)

    with c1:
        folium_static(density_map, width=1200, height=800)

    return None

# ===========================================================================================

@st.cache(show_spinner=False)
def get_file_content_as_string(path):
    url = '' + path
    response = urllib.request.urlopen('.instructions.md')

    return response.read().decode("utf-8")

# ===================================================

# Path to the Streamlit public S3 bucket
DATA_URL_ROOT = ""

# External files to download.
EXTERNAL_DEPENDENCIES = {}
# ===================================================
# This is the main app app itself, which appears when the user selects "Run the app"..
if __name__ == '__main__':
    main()
# ===================================================

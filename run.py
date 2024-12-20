import streamlit as st
import pandas as pd
import json
from datetime import datetime
from graph_geo_distribution import create_geo_distribution_map
from geo_utils import get_cached_coordinates, load_cache, save_cache
from graph_vehicles_fines import create_vehicle_fines_chart
from graph_common_infractions import create_common_infractions_chart
from graph_weekday_infractions import create_weekday_infractions_chart
from graph_fines_accumulated import create_fines_accumulated_chart
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
import io
import plotly.express as px
from folium import Map, Marker, Popup
from folium.features import CustomIcon
from streamlit_folium import st_folium

CACHE_FILE = "coordinates_cache.json"

def load_cache():
    """Carregar o cache de coordenadas de um arquivo JSON."""
    try:
        with open(CACHE_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_cache(cache):
    """Salvar o cache de coordenadas em um arquivo JSON."""
    with open(CACHE_FILE, "w") as file:
        json.dump(cache, file, indent=4)

def download_file_from_drive(file_id, credentials_info):
    """Download a file from Google Drive using its file ID."""
    credentials = Credentials.from_service_account_info(credentials_info)
    drive_service = build('drive', 'v3', credentials=credentials)
    request = drive_service.files().get_media(fileId=file_id)
    file_buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(file_buffer, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    file_buffer.seek(0)
    return file_buffer


def preprocess_data(file_buffer):
    """Preprocess the data from the file buffer."""
    data = pd.read_excel(file_buffer)
    data.columns = range(len(data.columns))  # Reindex columns

    for col_index in [13, 14]:
        data[col_index] = (
            data[col_index]
            .astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )

    # Garantir que índice 9 seja tratado como datetime
    data[9] = pd.to_datetime(data[9], errors='coerce', dayfirst=True)

    return data


def ensure_coordinates(data, cache, api_key):
    """Ensure Latitude and Longitude columns are populated."""
    def get_coordinates_with_cache(location):
        if location not in cache:
            cache[location] = get_cached_coordinates(location, api_key, cache)
        return cache[location]

    # Aplicar coordenadas para cada local no índice 12
    data[['Latitude', 'Longitude']] = data[12].apply(
        lambda loc: pd.Series(get_coordinates_with_cache(loc))
    )
    save_cache(cache)  # Salvar coordenadas atualizadas no cache
    return data

# Load secrets with error handling
try:
    drive_credentials = json.loads(st.secrets["general"]["CREDENTIALS"])
    drive_file_id = st.secrets["file_data"]["ultima_planilha_id"]
    api_key = st.secrets["general"]["API_KEY"]
except KeyError as e:
    st.error(f"Erro ao carregar os segredos: {e}")
    st.stop()

# Streamlit setup
st.set_page_config(page_title="Multas Dashboard", layout="wide")

# CSS Styling
st.markdown(
    """
    <style>
        .titulo-dashboard-container {
            display: flex;
            flex-direction: column; /* Alinha os itens na vertical */
            justify-content: center;
            align-items: center;
            text-align: center;
            margin: 0 auto;
            padding: 25px 20px;
            background: linear-gradient(to right, #F37529, rgba(255, 255, 255, 0.8));
            border-radius: 15px;
            box-shadow: 0 6px 10px rgba(0, 0, 0, 0.3);
        }
        .titulo-dashboard {
            font-size: 50px;
            font-weight: bold;
            color: #F37529;
            text-transform: uppercase;
            margin: 0;
        }
        .subtitulo-dashboard {
            font-size: 18px; /* Tamanho da fonte do subtítulo */
            color: #555555; /* Cor do subtítulo */
            margin: 10px 0 0 0; /* Espaçamento acima do subtítulo */
        }
        .logo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
            margin-bottom: 20px;
        }
        .logo-container img {
            max-width: 200px;
            height: auto;
        }
        .indicadores-container {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 40px;
            margin-top: 30px;
        }
        .indicador {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background-color: #FFFFFF;
            border: 4px solid #0066B4;
            border-radius: 15px;
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.3);
            width: 260px;
            height: 160px;
            padding: 10px;
        }
        .indicador span {
            font-size: 18px;
            color: #0066B4;
        }
        .indicador p {
            font-size: 38px;
            color: #0066B4;
            margin: 0;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Logo
st.markdown(
    f"""
    <div class="logo-container">
        <img src="{st.secrets['image']['logo_url']}" alt="Logo da Empresa">
    </div>
    """,
    unsafe_allow_html=True,
)

# Logo and Header
st.markdown(
    f"""
    <div class="titulo-dashboard-container">
        <h1 class="titulo-dashboard">Torre de Controle Itracker - Dashboard de Multas</h1>
        <p class="subtitulo-dashboard">Monitorando em tempo real as consultas de multas no DETRAN-RJ</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Load and preprocess data
st.info("Carregando dados do Google Drive...")
file_buffer = download_file_from_drive(drive_file_id, drive_credentials)
data = preprocess_data(file_buffer)

if data.empty:
    st.error("Os dados carregados estão vazios. Verifique o arquivo de origem.")
    st.stop()

# Ensure required columns
required_columns = [1, 5, 12, 14, 9]
missing_columns = [col for col in required_columns if col not in data.columns]
if missing_columns:
    st.error(f"As seguintes colunas estão ausentes: {missing_columns}")
    st.stop()

# Filters
data_inicio = st.date_input("Data de Início", value=datetime(datetime.now().year, 1, 1))
data_fim = st.date_input("Data Final", value=datetime.now())
filtered_data = data[
    (data[9] >= pd.Timestamp(data_inicio)) & 
    (data[9] <= pd.Timestamp(data_fim))
]

# Ensure coordinates and cache
cache = load_cache()  # Carregar coordenadas do cache
filtered_data = ensure_coordinates(filtered_data, cache, api_key)

st.markdown(
    """
    <h2 style="
        text-align: center; 
        color: #0066B4; 
        border-bottom: 2px solid #0066B4; 
        padding-bottom: 5px; 
        margin: 20px auto; 
        display: block; 
        width: 100%; 
    ">
        Indicadores Principais
    </h2>
    """, 
    unsafe_allow_html=True
)


# Indicador 1: Total de Multas (Auto de Infração únicos)
total_multas = data[5].nunique()  # Contar registros únicos no índice 5

# Indicador 2: Valor Total das Multas (soma dos valores correspondentes no índice 14)
# Garantir que o índice 14 esteja em formato numérico
data[14] = pd.to_numeric(
    data[14]
    .astype(str)
    .str.replace(r'[^\d,.-]', '', regex=True)
    .str.replace(',', '.'),
    errors='coerce'
)

# Filtrar registros únicos com base no índice 5
unique_fines = data.drop_duplicates(subset=[5])

# Somar os valores no índice 14 dos registros únicos
valor_total_multas = unique_fines[14].sum()

# Indicador 3: Multas no Mês Atual
mes_atual = datetime.now().month
multas_mes_atual = filtered_data[9].dt.month.value_counts().get(mes_atual, 0)

# Indicador 4: Valor das Multas no Mês Atual
valor_multas_mes_atual = filtered_data[filtered_data[9].dt.month == mes_atual][14].sum()

# Indicador 5: Data da Consulta (primeiro registro do índice 0)
data_consulta = data.iloc[0, 0] if not data.empty else "N/A"

# Estrutura HTML para exibição dos indicadores
indicadores_html = f"""
<div class="indicadores-container">
    <div class="indicador">
        <span>Total de Multas</span>
        <p>{total_multas}</p>
    </div>
    <div class="indicador">
        <span>Valor Total das Multas</span>
        <p>R$ {valor_total_multas:,.2f}</p>
    </div>
    <div class="indicador">
        <span>Multas no Mês Atual</span>
        <p>{multas_mes_atual}</p>
    </div>
    <div class="indicador">
        <span>Valor das Multas no Mês Atual</span>
        <p>R$ {valor_multas_mes_atual:,.2f}</p>
    </div>
    <div class="indicador">
        <span>Data da Consulta</span>
        <p>{data_consulta}</p>
    </div>
</div>
"""
st.markdown(indicadores_html, unsafe_allow_html=True)

st.markdown(
    """
    <h2 style="
        text-align: center; 
        color: #0066B4; 
        border-bottom: 2px solid #0066B4; 
        padding-bottom: 5px; 
        margin: 20px auto; 
        display: block; 
        width: 100%; 
    ">
        Distribuição Geográfica
    </h2>
    """, 
    unsafe_allow_html=True
)


# Configurar local inicial do mapa com base nas coordenadas médias das multas
if not filtered_data.empty and 'Latitude' in filtered_data.columns and 'Longitude' in filtered_data.columns:
    avg_lat = filtered_data['Latitude'].mean()
    avg_lon = filtered_data['Longitude'].mean()
else:
    avg_lat, avg_lon = -23.5505, -46.6333  # Coordenadas padrão (São Paulo)

m = Map(location=[avg_lat, avg_lon], zoom_start=8, tiles="CartoDB dark_matter")

# Ícone personalizado
icon_url = "https://cdn-icons-png.flaticon.com/512/1828/1828843.png"
icon_size = (30, 30)

# Adicionar marcadores ao mapa
for _, row in filtered_data.iterrows():
    if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
        popup_content = f"""
        <b>Local:</b> {row[12]}<br>
        <b>Valor:</b> R$ {row[14]:,.2f}<br>
        <b>Data da Infração:</b> {row[9].strftime('%d/%m/%Y') if pd.notnull(row[9]) else "Não disponível"}
        """
        marker_icon = CustomIcon(icon_url, icon_size=icon_size)
        Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=Popup(popup_content, max_width=300),
            icon=marker_icon
        ).add_to(m)

# Detalhes das multas para localização selecionada
map_click_data = st_folium(m, width="100%", height=600)  # Captura os cliques no mapa

if map_click_data and map_click_data.get("last_object_clicked"):
    lat = map_click_data["last_object_clicked"].get("lat")
    lng = map_click_data["last_object_clicked"].get("lng")
    
    # Filtrar multas pela localização clicada
    selected_fines = filtered_data[
        (filtered_data['Latitude'] == lat) & 
        (filtered_data['Longitude'] == lng)
    ]

    if not selected_fines.empty:
        st.markdown(
            """
            <h2 style="
                text-align: center; 
                color: #0066B4; 
                border-bottom: 2px solid #0066B4; 
                padding-bottom: 5px; 
                margin: 20px auto; 
                display: block; 
                width: 100%; 
            ">
                Detalhes das Multas para a Localização Selecionada
            </h2>
            """, 
            unsafe_allow_html=True
        )

        # Exibir detalhes das multas no DataFrame
        st.dataframe(
            selected_fines[[1, 12, 14, 9, 11]].rename(
                columns={
                    1: 'Placa Relacionada',
                    12: 'Local da Infração',
                    14: 'Valor a ser pago R$',
                    9: 'Data da Infração',
                    11: 'Descrição'
                }
            ).reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma multa encontrada para a localização selecionada.")

# Graphs Section
# Gráfico de Veículos com Mais Multas - Ajustado para Multas Únicas
st.markdown(
    """
    <h2 style="
        text-align: center; 
        color: #0066B4; 
        border-bottom: 2px solid #0066B4; 
        padding-bottom: 5px; 
        margin: 20px auto; 
        display: block; 
        width: 100%; 
    ">
        Veículos com Mais Multas
    </h2>
    """, 
    unsafe_allow_html=True
)


# Filtrar apenas multas únicas com base no índice 5 (Auto de Infração)
unique_fines = filtered_data.drop_duplicates(subset=[5])

# Agrupar multas por placa (índice 1) e calcular o total de multas e o valor total
vehicle_summary = (
    unique_fines.groupby(1)
    .agg(
        Numero_de_Multas=(5, 'count'),  # Contar multas únicas
        Valor_Total=(14, 'sum')        # Somar o valor das multas
    )
    .reset_index()
    .rename(columns={1: 'Placa do Veículo'})
)

# Ordenar os dados pelo valor total em ordem decrescente
vehicle_summary = vehicle_summary.sort_values(by='Valor_Total', ascending=False)

# Criar o gráfico de barras
fig = px.bar(
    vehicle_summary.head(10),  # Mostrar as 10 principais placas
    x='Placa do Veículo',
    y='Valor_Total',
    color='Numero_de_Multas',
    text='Numero_de_Multas',
    title='',
    labels={'Valor_Total': 'Total das Multas (R$)', 'Numero_de_Multas': 'Número de Multas'}
)

# Atualizar layout para personalização
fig.update_traces(texttemplate='%{text} multas<br>R$ %{y:,.2f}', textposition='outside')
fig.update_layout(
    xaxis_title="Placa do Veículo",
    yaxis_title="Total das Multas (R$)",
    legend_title="Número de Multas",
    template="plotly_white"
)

# Mostrar o gráfico no Streamlit
st.plotly_chart(fig, use_container_width=True)


# Infrações Mais Comuns
required_columns = [8, 11, 5]
missing_columns = [col for col in required_columns if col not in filtered_data.columns]
if not missing_columns:
    st.markdown(
        """
        <h2 style="
            text-align: center; 
            color: #0066B4; 
            border-bottom: 2px solid #0066B4; 
            padding-bottom: 5px; 
            margin: 20px auto; 
            display: block; 
            width: 100%; 
        ">
            Infrações Mais Comuns
        </h2>
        """, 
        unsafe_allow_html=True
    )

    filtered_infractions_data = filtered_data[required_columns]
    common_infractions_chart = create_common_infractions_chart(filtered_infractions_data)
    st.plotly_chart(common_infractions_chart, use_container_width=True)
else:
    st.error(f"As colunas com os índices {missing_columns} não foram encontradas nos dados.")

# Distribuição por Dias da Semana
if 9 in filtered_data.columns:
    st.markdown(
        """
        <h2 style="
            text-align: center; 
            color: #0066B4; 
            border-bottom: 2px solid #0066B4; 
            padding-bottom: 5px; 
            margin: 20px auto; 
            display: block; 
            width: 100%; 
        ">
            Distribuição por Dia da Semana
        </h2>
        """, 
        unsafe_allow_html=True
    )

    # Filtrar registros únicos com base no índice do Auto de Infração (5)
    unique_fines_weekday = filtered_data.drop_duplicates(subset=[5])

    # Mapear os nomes dos dias da semana para português manualmente
    day_translation = {
        "Monday": "Segunda-feira",
        "Tuesday": "Terça-feira",
        "Wednesday": "Quarta-feira",
        "Thursday": "Quinta-feira",
        "Friday": "Sexta-feira",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
    }

    # Agrupar por dia da semana
    weekday_summary = (
        unique_fines_weekday[9]
        .dt.day_name()  # Obter o nome dos dias em inglês
        .map(day_translation)  # Traduzir os nomes para português
        .value_counts()
        .reindex(
            ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"],
            fill_value=0  # Garantir que todos os dias apareçam, mesmo sem registros
        )
    )

    # Converter para DataFrame para uso no gráfico
    weekday_summary_df = weekday_summary.reset_index()
    weekday_summary_df.columns = ['Dia da Semana', 'Quantidade de Multas']

    # Criar o gráfico
    import plotly.express as px

    weekday_chart = px.bar(
        weekday_summary_df,
        x='Dia da Semana',
        y='Quantidade de Multas',
        title='',
        labels={'Quantidade de Multas': 'Quantidade de Multas'},
        text='Quantidade de Multas',
    )

    weekday_chart.update_traces(textposition='outside')
    weekday_chart.update_layout(
        xaxis_title="",
        yaxis_title="Quantidade de Multas",
        template="plotly_white",
    )

    st.plotly_chart(weekday_chart, use_container_width=True)
else:
    st.error("A coluna com índice 9 (Data da Infração) não foi encontrada nos dados.")

# Multas Acumuladas
if 9 in filtered_data.columns:
    st.markdown(
        """
        <h2 style="
            text-align: center; 
            color: #0066B4; 
            border-bottom: 2px solid #0066B4; 
            padding-bottom: 5px; 
            margin: 20px auto; 
            display: block; 
            width: 100%; 
        ">
            Multas Acumuladas
        </h2>
        """, 
        unsafe_allow_html=True
    )

    fines_accumulated_chart = create_fines_accumulated_chart(filtered_data)
    st.plotly_chart(fines_accumulated_chart, use_container_width=True)
else:
    st.error("A coluna com índice 9 (Data da Infração) não foi encontrada nos dados.")
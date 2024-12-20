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
from folium import Map, Marker, Popup
from folium.features import CustomIcon
from streamlit_folium import st_folium


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

    data.loc[:, ['Latitude', 'Longitude']] = data[12].apply(
        lambda loc: pd.Series(get_coordinates_with_cache(loc))
    )
    save_cache(cache)
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
        <span>Monitorando em tempo real as consultas de multas no DETRAN-RJ</span>
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

# Indicadores Principais - Atualizado
st.markdown("<h2 class='titulo-secao'>Indicadores Principais</h2>", unsafe_allow_html=True)

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

# Map Section
st.markdown('<h2 style="text-align: center; color: #0066B4;">Distribuição Geográfica</h2>', unsafe_allow_html=True)
m = Map(location=[-23.5505, -46.6333], zoom_start=5, tiles="CartoDB dark_matter")
icon_url = "https://cdn-icons-png.flaticon.com/512/1828/1828843.png"
icon_size = (30, 30)
for _, row in filtered_data.iterrows():
    if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
        popup_content = f"""
        <b>Local:</b> {row[12]}<br>
        <b>Valor:</b> R$ {row[14]:.2f}<br>
        <b>Data da Infração:</b> {row[9].strftime('%d/%m/%Y') if pd.notnull(row[9]) else "Não disponível"}
        """
        marker_icon = CustomIcon(icon_url, icon_size=icon_size)
        Marker(location=[row['Latitude'], row['Longitude']], popup=Popup(popup_content, max_width=300), icon=marker_icon).add_to(m)

st_folium(m, width="100%", height=600)

# Graphs Section
st.markdown("<h2 style='text-align: center; color: #0066B4;'>Veículos com Mais Multas</h2>", unsafe_allow_html=True)
vehicle_fines_chart = create_vehicle_fines_chart(filtered_data)
st.plotly_chart(vehicle_fines_chart, use_container_width=True)

# Infrações Mais Comuns
required_columns = [8, 11, 5]
missing_columns = [col for col in required_columns if col not in filtered_data.columns]
if not missing_columns:
    st.markdown("<h2 style='text-align: center; color: #0066B4;'>Infrações Mais Comuns</h2>", unsafe_allow_html=True)
    filtered_infractions_data = filtered_data[required_columns]
    common_infractions_chart = create_common_infractions_chart(filtered_infractions_data)
    st.plotly_chart(common_infractions_chart, use_container_width=True)
else:
    st.error(f"As colunas com os índices {missing_columns} não foram encontradas nos dados.")

# Distribuição por Dias da Semana
if 9 in filtered_data.columns:
    st.markdown("<h2 style='text-align: center; color: #0066B4;'>Distribuição por Dias da Semana</h2>", unsafe_allow_html=True)
    weekday_infractions_chart = create_weekday_infractions_chart(filtered_data)
    st.plotly_chart(weekday_infractions_chart, use_container_width=True)
else:
    st.error("A coluna com índice 9 (Data da Infração) não foi encontrada nos dados.")

# Multas Acumuladas
if 9 in filtered_data.columns:
    st.markdown("<h2 style='text-align: center; color: #0066B4;'>Multas Acumuladas</h2>", unsafe_allow_html=True)
    fines_accumulated_chart = create_fines_accumulated_chart(filtered_data)
    st.plotly_chart(fines_accumulated_chart, use_container_width=True)
else:
    st.error("A coluna com índice 9 (Data da Infração) não foi encontrada nos dados.")

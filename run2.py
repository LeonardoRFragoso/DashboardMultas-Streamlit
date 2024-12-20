import streamlit as st
import pandas as pd
import json
from datetime import datetime
from graph_geo_distribution import create_geo_distribution_map
from geo_utils import get_cached_coordinates
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

def load_cache():
    """Load coordinates cache from a JSON file."""
    try:
        with open("coordinates_cache.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_cache(cache):
    """Save coordinates cache to a JSON file."""
    with open("coordinates_cache.json", "w") as file:
        json.dump(cache, file)

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
    data.columns = range(len(data.columns))

    for col_index in [13, 14]:
        data[col_index] = (
            data[col_index]
            .astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )

    data[9] = pd.to_datetime(data[9], errors='coerce', dayfirst=True)

    return data

# Load secrets
drive_credentials = st.secrets["general"]["CREDENTIALS"]
drive_file_id = st.secrets["file_data"]["ultima_planilha_id"]
api_key = st.secrets["general"]["API_KEY"]

st.set_page_config(page_title="Multas Dashboard", layout="wide")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="logo-container">
        <img src="{st.secrets['image']['logo_url']}" alt="Logo da Empresa">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="display: flex; justify-content: center; align-items: center; text-align: center; margin: 0 auto; background: linear-gradient(to right, #F37529, rgba(255, 255, 255, 0.8)); border-radius: 15px; padding: 20px;">
        <h1 style="font-size: 36px; color: #FFFFFF; text-transform: uppercase; margin: 0;">Dashboard de Multas</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.info("Carregando dados do Google Drive...")
file_buffer = download_file_from_drive(drive_file_id, eval(drive_credentials))
data = preprocess_data(file_buffer)
st.info("Dados carregados corretamente")

# Filtros
data_inicio = st.date_input("Data de Início", value=datetime(datetime.now().year, 1, 1))
data_fim = st.date_input("Data Final", value=datetime.now())

if st.button("Aplicar Filtros"):
    filtered_data = data[
        (data[9] >= pd.Timestamp(data_inicio)) &
        (data[9] <= pd.Timestamp(data_fim))
    ]
else:
    filtered_data = data.copy()

filtered_data.rename(columns={
    12: 'Local da Infração',
    14: 'Valor a ser pago R$',
    1: 'Placa Relacionada',
    2: 'Auto de Infração',
    9: 'Data da Infração',
    7: 'Enquadramento da Infração',
    8: 'Descrição'
}, inplace=True)

# Garantir que Latitude e Longitude existam
if 'Local da Infração' in filtered_data.columns:
    cache = load_cache()
    def get_coordinates_with_cache(location):
        if location not in cache:
            cache[location] = get_cached_coordinates(location, api_key, cache)
        return cache[location]

    filtered_data[['Latitude', 'Longitude']] = filtered_data['Local da Infração'].apply(
        lambda loc: pd.Series(get_coordinates_with_cache(loc))
    )
    save_cache(cache)
else:
    filtered_data['Latitude'] = None
    filtered_data['Longitude'] = None

# Determinar localização inicial do mapa
valid_coordinates = filtered_data.dropna(subset=['Latitude', 'Longitude'])
if not valid_coordinates.empty:
    map_center = [
        valid_coordinates['Latitude'].mean(),
        valid_coordinates['Longitude'].mean()
    ]
else:
    map_center = [-23.5505, -46.6333]  # São Paulo, Brasil

# Indicadores principais
st.markdown("<h2 style='text-align: center; color: #0066B4;'>Indicadores Principais</h2>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

# Total de multas
total_multas = data[5].nunique()
col1.metric("Total de Multas", total_multas)

# Valor total das multas
valor_total_multas = data.drop_duplicates(subset=[5])[14].sum()
col2.metric("Valor Total das Multas", f"R$ {valor_total_multas:,.2f}")

# Multas no mês atual
mes_atual = datetime.now().month
ano_atual = datetime.now().year
multas_mes_atual = data[(data[9].dt.month == mes_atual) & (data[9].dt.year == ano_atual)][5].nunique()
col3.metric("Multas no Mês Atual", multas_mes_atual)

# Valor total das multas no mês atual
valor_multas_mes_atual = data[(data[9].dt.month == mes_atual) & (data[9].dt.year == ano_atual)][14].sum()
col4.metric("Valor das Multas no Mês Atual", f"R$ {valor_multas_mes_atual:,.2f}")

# Data da consulta
data_consulta = data.iloc[1, 0] if not data.empty else "N/A"
col5.metric("Data da Consulta", data_consulta)

# Map Section
st.markdown('<h2 style="text-align: center; color: #0066B4;">Distribuição Geográfica</h2>', unsafe_allow_html=True)
m = Map(location=map_center, zoom_start=5, tiles="CartoDB dark_matter")

icon_url = "https://cdn-icons-png.flaticon.com/512/1828/1828843.png"
icon_size = (30, 30)  # Tamanho ajustado do ícone

for _, row in filtered_data.iterrows():
    if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
        popup_content = f"""
        <b>Local:</b> {row['Local da Infração']}<br>
        <b>Valor:</b> R$ {row['Valor a ser pago R$']:.2f}<br>
        <b>Data da Infração:</b> {row['Data da Infração'].strftime('%d/%m/%Y') if pd.notnull(row['Data da Infração']) else "Não disponível"}
        """
        marker_icon = CustomIcon(icon_url, icon_size=icon_size)
        Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=Popup(popup_content, max_width=300),
            icon=marker_icon
        ).add_to(m)

st_folium(m, width="100%", height=600)

# Graphs Section
st.markdown("<h2 style='text-align: center; color: #0066B4;'>Veículos com Mais Multas</h2>", unsafe_allow_html=True)
vehicle_fines_chart = create_vehicle_fines_chart(filtered_data)
st.plotly_chart(vehicle_fines_chart, use_container_width=True)

# Preparar dados para "Infrações Mais Comuns"
if 'Enquadramento da Infração' in filtered_data.columns:
    common_infractions_data = filtered_data.groupby(['Enquadramento da Infração', 'Descrição']).size().reset_index(name='Ocorrências')
    common_infractions_data = common_infractions_data.sort_values(by='Ocorrências', ascending=False)

    st.markdown("<h2 style='text-align: center; color: #0066B4;'>Infrações Mais Comuns</h2>", unsafe_allow_html=True)
    common_infractions_chart = create_common_infractions_chart(common_infractions_data)
    st.plotly_chart(common_infractions_chart, use_container_width=True)
else:
    st.error("Coluna 'Enquadramento da Infração' não encontrada nos dados carregados.")

st.markdown("<h2 style='text-align: center; color: #0066B4;'>Distribuição por Dias da Semana</h2>", unsafe_allow_html=True)
weekday_infractions_chart = create_weekday_infractions_chart(filtered_data)
st.plotly_chart(weekday_infractions_chart, use_container_width=True)

st.markdown("<h2 style='text-align: center; color: #0066B4;'>Multas Acumuladas</h2>", unsafe_allow_html=True)
fines_accumulated_chart = create_fines_accumulated_chart(filtered_data)
st.plotly_chart(fines_accumulated_chart, use_container_width=True)

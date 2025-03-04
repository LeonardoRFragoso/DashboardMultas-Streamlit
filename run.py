import streamlit as st
import pandas as pd
import json
from datetime import datetime
import io
import plotly.express as px
from folium import Map, Marker, Popup
from folium.features import CustomIcon
from streamlit_folium import st_folium
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Import custom modules
from graph_geo_distribution import create_geo_distribution_map
from geo_utils import get_cached_coordinates, initialize_cache
from graph_vehicles_fines import create_vehicle_fines_chart 
from graph_common_infractions import create_common_infractions_chart
from graph_weekday_infractions import create_weekday_infractions_chart
from graph_fines_accumulated import create_monthly_fines_chart, create_yearly_fines_chart
from indicators import render_indicators
from filters_module import apply_filters

# Inicializar cache
initialize_cache()

def download_file_from_drive(file_id, credentials_info):
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
    data = pd.read_excel(file_buffer)
    data.columns = range(len(data.columns))
    
    # Valores monetários (valor_original e valor_pagar)
    for col_index in [13, 14]:  # Correto, mantém
        data[col_index] = (
            data[col_index]
            .astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )
    
    # Data da infração
    data[9] = pd.to_datetime(data[9], errors='coerce', dayfirst=True)
    
    return data

def ensure_coordinates(data, api_key):
    def get_coordinates_with_cache(location):
        lat, lng = get_cached_coordinates(location, api_key)
        if lat is None or lng is None:
            return [float('nan'), float('nan')]
        return [lat, lng]

    if data.empty:
        st.warning("Nenhum dado disponível para processar coordenadas.")
        return data  # Retorna o DataFrame vazio sem erro

    if 12 not in data.columns:
        st.error("A coluna de Local da Infração (índice 12) não foi encontrada.")
        data[['Latitude', 'Longitude']] = float('nan')
        return data

    coordinates = data[12].apply(
        lambda loc: pd.Series(
            get_coordinates_with_cache(loc) if pd.notnull(loc) else [float('nan'), float('nan')]
        )
    )

    # Garantir que sempre haja duas colunas, mesmo que vazias
    if coordinates.shape[1] != 2:
        coordinates = pd.DataFrame([[float('nan'), float('nan')]] * len(data), columns=[0, 1])

    # Atribuir as coordenadas corretamente
    data[['Latitude', 'Longitude']] = coordinates

    return data

try:
    drive_credentials = json.loads(st.secrets["general"]["CREDENTIALS"])
    drive_file_id = st.secrets["file_data"]["ultima_planilha_id"]
    api_key = st.secrets["general"]["API_KEY"]
except KeyError as e:
    st.error(f"Erro ao carregar os segredos: {e}")
    st.stop()

st.set_page_config(page_title="Multas Dashboard", layout="wide")

# UI e estilo original completo
st.markdown(
    """
    <style>
        /* Estilização para o expander (filtros) */
        .filter-expander {
            border: 2px solid #F37529;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }

        [data-testid="stExpander"] > summary {
            font-weight: 600;
            font-size: 16px;
            color: #F37529;
            padding: 12px;
            cursor: pointer;
        }

        /* Alerta sutil para uso de filtros */
        .filtro-alerta {
            text-align: center;
            color: #F37529;
            font-size: 15px;
            margin-bottom: 15px;
            font-weight: 500;
        }

        /* Container e estilo do título principal */
        .titulo-dashboard-container {
            display: flex;
            flex-direction: column;
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
            font-size: 18px;
            color: #555555;
            margin: 10px 0 0 0;
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

        /* Estilização dos indicadores principais */
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
            font-size: 22px;
            color: #0066B4;
            margin: 0;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="logo-container">
        <img src="{st.secrets['image']['logo_url']}" alt="Logo da Empresa">
    </div>
    <div class="titulo-dashboard-container">
        <h1 class="titulo-dashboard">Torre de Controle Itracker - Dashboard de Multas</h1>
        <p class="subtitulo-dashboard">Monitorando em tempo real as consultas de multas no DETRAN-RJ</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Carregar e processar dados
file_buffer = download_file_from_drive(drive_file_id, drive_credentials)
data = preprocess_data(file_buffer)

if data.empty:
    st.error("Os dados carregados estão vazios.")
    st.stop()

# Aplicar filtros
filtered_data = apply_filters(data)

# Verificar se há dados após filtragem
if filtered_data.empty:
    st.warning("Nenhuma multa encontrada com os filtros selecionados. Tente ajustar os filtros.")
    st.stop()

# Garantir coordenadas com cache
filtered_data = ensure_coordinates(filtered_data, api_key)

# Renderizar Indicadores
render_indicators(data, filtered_data, None, None)

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
map_click_data = st_folium(m, width="100%", height=1000)  # Captura os cliques no mapa

if map_click_data and map_click_data.get("last_object_clicked"):
    lat = map_click_data["last_object_clicked"].get("lat")
    lng = map_click_data["last_object_clicked"].get("lng")
    
    # Filtrar multas pela localização clicada
    selected_fines = filtered_data[
        (filtered_data['Latitude'] == lat) & 
        (filtered_data['Longitude'] == lng)
    ]

    # Remover duplicatas baseado no Auto de Infração (índice 5)
    selected_fines = selected_fines.drop_duplicates(subset=[5])

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
required_columns = [8, 11, 5]  # Código da infração, Descrição, Auto de Infração
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

    # Filtrar registros únicos com base no índice Auto de Infração (5)
    unique_infractions = filtered_data.drop_duplicates(subset=[5])

    # Selecionar apenas as colunas necessárias
    filtered_infractions_data = unique_infractions[required_columns]

    # Criar o gráfico de infrações mais comuns
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
if 9 in filtered_data.columns and 14 in filtered_data.columns and 5 in filtered_data.columns:
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

    try:
              
        # Remover duplicados com base no Auto de Infração (índice 5)
        unique_fines_accumulated = filtered_data.drop_duplicates(subset=[5])

        # Encontrar o ano mais antigo e mais recente nos dados
        min_year = unique_fines_accumulated[9].dt.year.min()
        max_year = unique_fines_accumulated[9].dt.year.max()
        
        if pd.isna(min_year):
            min_year = datetime.now().year
        if pd.isna(max_year):
            max_year = datetime.now().year

        # Criar uma lista de todos os meses do período
        all_months = pd.period_range(
            start=f"{min_year}-01", 
            end=f"{max_year}-12", 
            freq="M"
        )

        # Agrupar os dados por mês e calcular os totais
        accumulated_summary = (
            unique_fines_accumulated.groupby(unique_fines_accumulated[9].dt.to_period("M"))
            .agg(
                Quantidade_de_Multas=(5, 'count'),  # Contar Auto de Infração únicos
                Valor_Total=(14, 'sum')            # Somar os valores das multas
            )
            .reset_index()
        )

        # Ajustar o índice para incluir todos os meses do período
        accumulated_summary.set_index(9, inplace=True)
        accumulated_summary = accumulated_summary.reindex(all_months, fill_value=0).reset_index()
        accumulated_summary.rename(columns={"index": "Período"}, inplace=True)

        # Converter o período para formato de data para o gráfico
        accumulated_summary["Período"] = accumulated_summary["Período"].dt.to_timestamp()

        # Criar o gráfico de linha
        accumulated_chart = px.line(
            accumulated_summary,
            x="Período",
            y=['Quantidade_de_Multas', 'Valor_Total'],
            title="Evolução Mensal de Multas",
            labels={
                "value": "Valores",
                "variable": "Métricas",
                "Período": "Período"
            },
            markers=True,
        )

        # Ajustar layout do gráfico
        accumulated_chart.update_traces(marker=dict(size=8))
        accumulated_chart.update_layout(
            xaxis_title="",
            yaxis_title="Valores",
            template="plotly_white",
            legend_title="Métricas",
            height=400
        )
        
        st.plotly_chart(accumulated_chart, use_container_width=True)

        # Gráfico Mensal com Seletor de Ano
        st.markdown("#### Análise Mensal de Multas")
        create_monthly_fines_chart(unique_fines_accumulated)

        # Gráfico Anual com Seletor de Período
        st.markdown("#### Análise Anual de Multas")
        create_yearly_fines_chart(unique_fines_accumulated)

    except Exception as e:
        st.error(f"Erro ao processar dados de multas acumuladas: {str(e)}")
        st.write("Detalhes do erro:", e)
else:
    st.error("As colunas necessárias para o gráfico de multas acumuladas não foram encontradas.")
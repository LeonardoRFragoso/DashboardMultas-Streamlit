import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

def handle_table_display(df, columns_to_display, rename_map=None):
    display_df = df[columns_to_display].copy()
    if rename_map:
        display_df = display_df.rename(columns=rename_map)

    if 14 in columns_to_display:
        display_df[rename_map[14]] = display_df[rename_map[14]].apply(lambda x: f'R$ {x:,.2f}')

    if 0 in columns_to_display:
        display_df[rename_map[0]] = pd.to_datetime(display_df[rename_map[0]]).dt.strftime('%d/%m/%Y')

    st.markdown(
        """
        <style>
            [data-testid="stTable"] table {
                width: 100% !important;
            }
            [data-testid="stTable"] td, [data-testid="stTable"] th {
                white-space: nowrap;
                min-width: 120px;
            }
            div[data-testid="stDataFrame"] > div {
                width: 100% !important;
            }
            div[data-testid="stDataFrame"] > div > iframe {
                width: 100% !important;
                min-width: 100% !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    return st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        height=500
    )

def render_css():
    st.markdown(
        """
        <style>
            .indicadores-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
                justify-content: center;
                gap: 25px;
                margin-top: 30px;
                max-width: 1600px;
                margin-left: auto;
                margin-right: auto;
            }

            .indicador {
                background-color: #FFFFFF;
                border: 4px solid #0066B4;
                border-radius: 15px;
                box-shadow: 0 8px 12px rgba(0, 0, 0, 0.3);
                text-align: center;
                padding: 20px;
                width: 100%;
                max-width: 210px;
                height: 140px;
                cursor: pointer;
                transition: transform 0.2s ease-in-out;
                margin: 0 auto 5px auto;
            }

            .button-container {
                width: 100%;
                max-width: 210px;
                margin: 0 auto;
            }

            .stButton > button {
                background-color: #F37529 !important;
                color: white !important;
                font-weight: 600 !important;
                width: 100% !important;
                max-width: 210px !important;
                margin: 5px auto !important;
                display: block !important;
            }

            .stButton > button:hover {
                background-color: #ff8c42 !important;
                transform: translateY(-2px) !important;
                transition: all 0.2s ease !important;
                box-shadow: 0 6px 16px rgba(243, 117, 41, 0.3) !important;
            }

            div[data-testid="column"] {
                padding: 0 !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
            }
            div[data-testid="stDataFrame"] > div {
                width: 100% !important;
            }
            div[data-testid="stDataFrame"] > div > iframe {
                width: 100% !important;
                min-width: 100% !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_indicators(data, filtered_data, data_inicio, data_fim):
    render_css()

    if 5 not in data.columns:
        st.error("A coluna com índice 5 não foi encontrada nos dados.")
        return

    column_map = {
        0: "Data",
        1: "Placa do Veículo",
        5: "Auto de Infração",
        14: "Valor"
    }

    try:
        unique_fines = data.drop_duplicates(subset=[5])
        
        total_multas = unique_fines[5].nunique()
        valor_total_multas = unique_fines[14].sum()
        ano_atual = datetime.now().year
        mes_atual = data_fim.month if data_fim else datetime.now().month

        multas_ano_atual = unique_fines[unique_fines[9].dt.year == ano_atual][5].nunique()
        valor_multas_ano_atual = unique_fines[unique_fines[9].dt.year == ano_atual][14].sum()

        multas_mes_atual = filtered_data[
            (filtered_data[9].dt.year == ano_atual) & 
            (filtered_data[9].dt.month == mes_atual)
        ][5].nunique()

        valor_multas_mes_atual = filtered_data[
            (filtered_data[9].dt.year == ano_atual) & 
            (filtered_data[9].dt.month == mes_atual)
        ][14].sum()

        data_consulta = data.iloc[1, 0]
        data_formatada = (
            data_consulta.strftime('%d/%m/%Y')
            if isinstance(data_consulta, pd.Timestamp) else str(data_consulta)
        )

        cols = st.columns(7)
        
        with cols[0]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Total de Multas</span>
                    <p>{total_multas}</p>
                </div>""", 
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="total_multas"):
                handle_table_display(unique_fines, [0, 1, 5], column_map)

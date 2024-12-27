import streamlit as st
import pandas as pd
from datetime import datetime

@st.cache_data(ttl=3600)
def calculate_indicators(data, filtered_data, data_inicio, data_fim):
    try:
        if 5 not in data.columns:
            return None
            
        data_copy = data.copy()
        filtered_copy = filtered_data.copy()
        unique_fines = data_copy.drop_duplicates(subset=[5])
        ano_atual = datetime.now().year
        mes_atual = data_fim.month if data_fim else datetime.now().month
        
        return {
            'total_multas': unique_fines[5].nunique(),
            'valor_total_multas': unique_fines[14].sum(),
            'multas_ano_atual': unique_fines[unique_fines[9].dt.year == ano_atual][5].nunique(),
            'valor_multas_ano_atual': unique_fines[unique_fines[9].dt.year == ano_atual][14].sum(),
            'multas_mes_atual': filtered_copy[
                (filtered_copy[9].dt.year == ano_atual) & 
                (filtered_copy[9].dt.month == mes_atual)
            ][5].nunique(),
            'valor_multas_mes_atual': filtered_copy[
                (filtered_copy[9].dt.year == ano_atual) & 
                (filtered_copy[9].dt.month == mes_atual)
            ][14].sum(),
            'data_consulta': format_date(data_copy.iloc[1, 0]) if not data_copy.empty else "N/A"
        }
    except Exception as e:
        st.error(f"Erro ao calcular indicadores: {str(e)}")
        return None

def format_date(date):
    try:
        return pd.to_datetime(date, format='%d/%m/%Y', dayfirst=True).strftime('%d/%m/%Y')
    except:
        return str(date)

def handle_table_display(df, columns_to_display, rename_map=None):
    display_df = df[columns_to_display].copy()
    if rename_map:
        display_df = display_df.rename(columns=rename_map)

    # Formatando valores monetários
    if 14 in columns_to_display:
        # Converter para string após formatação para evitar erro de tipo
        display_df.loc[:, rename_map[14]] = display_df[rename_map[14]].apply(
            lambda x: f'R$ {x:,.2f}' if pd.notnull(x) else 'R$ 0,00'
        ).astype(str)
    
    # Formatando datas
    if 0 in columns_to_display:
        display_df.loc[:, rename_map[0]] = pd.to_datetime(
            display_df[rename_map[0]], 
            format='%d/%m/%Y', 
            errors='coerce',
            dayfirst=True
        ).dt.strftime('%d/%m/%Y')

    st.markdown(
        """
        <style>
            /* Reset de margens e paddings */
            .element-container {padding: 0 !important; margin: 0 !important;}
            div[data-testid="stHorizontalBlock"] {gap: 0 !important; padding: 0 !important; margin: 0 !important;}
            
            /* Ajustes de tabela */
            [data-testid="column"] > div:has(div.stDataFrame) {width: 100% !important; max-width: 100% !important; padding: 0 !important; margin: 0 !important;}
            [data-testid="column"] > div > div.stDataFrame {width: 100% !important; max-width: 100% !important; padding: 0 !important; margin: 0 !important;}
            [data-testid="column"] > div > div.stDataFrame > div {width: 100% !important; max-width: 100% !important; padding: 0 !important; margin: 0 !important;}
            [data-testid="column"] > div > div.stDataFrame > div > iframe {
                width: 100% !important;
                min-width: 100% !important;
                height: calc(100vh - 300px) !important;
                min-height: 500px !important;
                border: none !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            .dataframe {
                width: 100% !important;
                font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
                border-collapse: collapse !important;
            }
            .dataframe th {
                background-color: #0066B4 !important;
                color: white !important;
                font-weight: 500 !important;
                padding: 12px 8px !important;
                white-space: nowrap !important;
                position: sticky !important;
                top: 0 !important;
                z-index: 1 !important;
            }
            .dataframe td {padding: 10px 8px !important; border-bottom: 1px solid #e0e0e0 !important; white-space: nowrap !important;}
            .dataframe tr:nth-child(even) {background-color: #f8f9fa !important;}
            .dataframe tr:hover {background-color: #f0f7ff !important;}
            iframe[data-testid="stDataFrame"] {width: 100% !important; min-width: 100% !important; border: none !important;}
        </style>
        <h2 style="text-align: center; color: #0066B4; border-bottom: 2px solid #0066B4; padding-bottom: 5px; margin: 5px 0; width: 100%;">
            Detalhes da Consulta
        </h2>
        """, 
        unsafe_allow_html=True
    )

    return st.dataframe(
        display_df.reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
        height=None
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

            .indicador:hover {
                transform: scale(1.05);
            }

            .indicador span {
                font-size: 18px;
                color: #0066B4;
            }

            .indicador p {
                font-size: 24px;
                color: #0066B4;
                margin: 0;
                font-weight: bold;
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
        data_copy = data.copy()
        filtered_data_copy = filtered_data.copy()
        indicators = calculate_indicators(data_copy, filtered_data_copy, data_inicio, data_fim)
        
        if not indicators:
            st.error("Erro ao calcular os indicadores")
            return

        unique_fines = data_copy.drop_duplicates(subset=[5])
        ano_atual = datetime.now().year
        mes_atual = data_fim.month if data_fim else datetime.now().month
        
        cols = st.columns(7)
        
        with cols[0]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Total de Multas</span>
                    <p>{indicators['total_multas']}</p>
                </div>""", 
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="total_multas"):
                handle_table_display(unique_fines, [0, 1, 5], column_map)

        with cols[1]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Valor Total das Multas</span>
                    <p>R$ {indicators['valor_total_multas']:,.2f}</p>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="valor_total"):
                handle_table_display(unique_fines, [0, 1, 5, 14], column_map)

        with cols[2]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Multas no Ano Atual</span>
                    <p>{indicators['multas_ano_atual']}</p>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="multas_ano"):
                ano_data = unique_fines[unique_fines[9].dt.year == ano_atual].copy()
                handle_table_display(ano_data, [0, 1, 5], column_map)

        with cols[3]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Valor Total Multas no Ano Atual</span>
                    <p>R$ {indicators['valor_multas_ano_atual']:,.2f}</p>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="valor_ano"):
                ano_data = unique_fines[unique_fines[9].dt.year == ano_atual].copy()
                handle_table_display(ano_data, [0, 1, 5, 14], column_map)

        with cols[4]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Multas no Mês Atual</span>
                    <p>{indicators['multas_mes_atual']}</p>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="multas_mes"):
                mes_data = filtered_data_copy[
                    (filtered_data_copy[9].dt.year == ano_atual) & 
                    (filtered_data_copy[9].dt.month == mes_atual)
                ].copy()
                handle_table_display(mes_data, [0, 1, 5], column_map)

        with cols[5]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Valor das Multas no Mês Atual</span>
                    <p>R$ {indicators['valor_multas_mes_atual']:,.2f}</p>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="valor_mes"):
                mes_data = filtered_data_copy[
                    (filtered_data_copy[9].dt.year == ano_atual) & 
                    (filtered_data_copy[9].dt.month == mes_atual)
                ].copy()
                handle_table_display(mes_data, [0, 1, 5, 14], column_map)

        with cols[6]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Data da Consulta</span>
                    <p>{indicators['data_consulta']}</p>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="data_consulta"):
                st.write(f"Período analisado: {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}")

    except Exception as e:
        st.error(f"Erro ao processar os dados: {str(e)}")
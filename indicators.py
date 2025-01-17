import streamlit as st
import pandas as pd
from datetime import datetime

def handle_details_display(df, columns_to_display, rename_map=None, title="Detalhamento dos Dados"):
    """Função auxiliar para exibir dados em um expander estilizado com colunas contextuais"""
    
    # Mapeamento expandido das colunas
    full_column_map = {
        0: "Dia da Consulta",
        1: "Placa do Veículo",
        2: "RENAVAM",
        3: "CNPJ",
        4: "Status",
        5: "Auto de Infração",
        6: "Auto de Renainf",
        7: "Data para Pagto c/ Desconto",
        8: "Enquadramento",
        9: "Data da Infração",
        10: "Hora",
        11: "Descrição",
        12: "Local da Infração",
        13: "Valor Original",
        14: "Valor a Pagar",
        15: "Status de Pagamento",
        16: "Órgão Emissor",
        17: "Agente Emissor"
    }
    
    # Define colunas contextuais baseado no título
    if "Total de Multas" in title:
        columns_to_display = [0, 1, 5, 8, 11, 12, 14, 15]  # Visão geral completa
    elif "Valor Total" in title:
        columns_to_display = [0, 1, 5, 13, 14, 15, 16]  # Foco em valores e pagamentos
    elif "Ano" in title:
        columns_to_display = [0, 1, 5, 8, 11, 14, 15, 16]  # Visão anual com detalhes
    elif "Mês" in title:
        columns_to_display = [0, 1, 5, 8, 11, 12, 14, 15, 16]  # Visão mensal detalhada
    
    display_df = df[columns_to_display].copy()
    rename_map = {col: full_column_map[col] for col in columns_to_display}
    display_df = display_df.rename(columns=rename_map)

    # Formatação de valores monetários e datas
    for col in display_df.columns:
        if "Valor" in col:
            display_df[col] = display_df[col].apply(lambda x: f'R$ {x:,.2f}')
        elif "Data" in col:
            display_df[col] = pd.to_datetime(display_df[col], format='%d/%m/%Y', dayfirst=True).dt.strftime('%d/%m/%Y')

    st.markdown("""
        <style>
            /* Container principal */
            div[data-testid="stExpander"] {
                border: none !important;
                border-radius: 12px !important;
                background: white !important;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
                margin: 1.5rem 0 !important;
                width: 100% !important;
            }
            
            /* Cabeçalho do expander */
            .streamlit-expanderHeader {
                background: linear-gradient(135deg, #0066B4, #0077CC) !important;
                color: white !important;
                padding: 1rem 1.5rem !important;
                font-size: 1.1rem !important;
                font-weight: 500 !important;
            }
            
            /* Container do conteúdo */
            .streamlit-expanderContent {
                padding: 0 !important;
                background: white !important;
                max-width: 100% !important;
                overflow: visible !important;
            }
            
            /* Container da tabela */
            div[data-testid="stDataFrame"] {
                width: 100% !important;
                max-width: 100% !important;
                overflow: visible !important;
            }
            
            /* Forçar largura total da tabela */
            .stDataFrame > div {
                width: 100% !important;
                max-width: 100% !important;
                overflow: visible !important;
            }
            
            /* Ajuste das colunas da tabela */
            div[data-testid="stDataFrame"] table {
                width: 100% !important;
                table-layout: auto !important;
            }
            
            /* Header da tabela */
            div[data-testid="stDataFrame"] th {
                background: #0066B4 !important;
                color: white !important;
                padding: 12px 8px !important;
                font-size: 0.9rem !important;
                font-weight: 500 !important;
                text-transform: none !important;
                white-space: normal !important;
                overflow: visible !important;
                text-overflow: clip !important;
                min-width: auto !important;
            }
            
            /* Células */
            div[data-testid="stDataFrame"] td {
                padding: 8px !important;
                font-size: 0.95rem !important;
                color: #333 !important;
                border-bottom: 1px solid #eef2f6 !important;
                white-space: normal !important;
                overflow: visible !important;
                text-overflow: clip !important;
                min-width: auto !important;
            }
            
            /* Linhas alternadas */
            div[data-testid="stDataFrame"] tr:nth-child(even) td {
                background-color: #f8faff !important;
            }
            
            /* Ajustes específicos para tipos de células */
            div[data-testid="stDataFrame"] td[data-type="Data"] {
                white-space: nowrap !important;
                width: 100px !important;
            }
            
            div[data-testid="stDataFrame"] td[data-type="Placa"] {
                width: 100px !important;
                white-space: nowrap !important;
            }
            
            div[data-testid="stDataFrame"] td[data-type="Auto"] {
                width: 120px !important;
                white-space: nowrap !important;
            }
            
            div[data-testid="stDataFrame"] td[data-type="Valor"] {
                width: 120px !important;
                text-align: right !important;
                font-family: monospace !important;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.expander(title, expanded=True):
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=350
        )

def render_css():
    st.markdown("""
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
    """, unsafe_allow_html=True)

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
        # Verificação de datas nulas
        if data_inicio is None or data_fim is None:
            data_inicio = datetime.now().replace(day=1)
            data_fim = datetime.now()

        # Cria DataFrame com valores únicos por auto de infração
        unique_fines = data.drop_duplicates(subset=[5])
        unique_filtered_data = filtered_data.drop_duplicates(subset=[5])
        
        # Cálculos com valores únicos
        total_multas = unique_fines[5].nunique()
        valor_total_multas = unique_fines[14].sum()
        ano_atual = datetime.now().year
        mes_atual = data_fim.month if data_fim else datetime.now().month

        # Filtragem para ano atual (valores únicos)
        multas_ano_atual = unique_fines[unique_fines[9].dt.year == ano_atual][5].nunique()
        valor_multas_ano_atual = unique_fines[unique_fines[9].dt.year == ano_atual][14].sum()

        # Filtragem para mês atual (valores únicos)
        mes_data = unique_filtered_data[
            (unique_filtered_data[9].dt.year == ano_atual) & 
            (unique_filtered_data[9].dt.month == mes_atual)
        ]
        multas_mes_atual = mes_data[5].nunique()
        valor_multas_mes_atual = mes_data[14].sum()

        # Data da última atualização
        data_atualizacao = data.iloc[0, 0] if not data.empty else pd.Timestamp.now()
        if isinstance(data_atualizacao, str):
            data_atualizacao = pd.to_datetime(data_atualizacao, format='%d/%m/%Y', dayfirst=True)
                
        # Container para os indicadores
        cols = st.columns(7)

        # Total de Multas
        with cols[0]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Total de Multas</span>
                    <p>{total_multas}</p>
                </div>""", 
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="total_multas"):
                handle_details_display(
                    unique_fines,
                    [0, 1, 5, 14],
                    column_map,
                    "Total de Multas"
                )

        # Valor Total das Multas
        with cols[1]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Valor Total das Multas</span>
                    <p>R$ {valor_total_multas:,.2f}</p>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="valor_total"):
                handle_details_display(
                    unique_fines,
                    [0, 1, 5, 14],
                    column_map,
                    "Valor Total das Multas"
                )

        # Multas no Ano
        with cols[2]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Multas no Ano ({ano_atual})</span>
                    <p>{multas_ano_atual}</p>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="multas_ano"):
                ano_data = unique_fines[unique_fines[9].dt.year == ano_atual]
                handle_details_display(
                    ano_data,
                    [0, 1, 5, 14],
                    column_map,
                    f"Multas do Ano {ano_atual}"
                )

        # Valor das Multas no Ano
        with cols[3]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Valor das Multas no Ano ({ano_atual})</span>
                    <p>R$ {valor_multas_ano_atual:,.2f}</p>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="valor_ano"):
                ano_data = unique_fines[unique_fines[9].dt.year == ano_atual]
                handle_details_display(
                    ano_data,
                    [0, 1, 5, 14],
                    column_map,
                    f"Valor das Multas do Ano {ano_atual}"
                )

        # Multas no Mês
        with cols[4]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Multas no Mês ({mes_atual:02d}/{ano_atual})</span>
                    <p>{multas_mes_atual}</p>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="multas_mes"):
                handle_details_display(
                    mes_data,
                    [0, 1, 5, 14],
                    column_map,
                    f"Multas do Mês {mes_atual:02d}/{ano_atual}"
                )

        # Valor das Multas no Mês
        with cols[5]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Valor das Multas no Mês ({mes_atual:02d}/{ano_atual})</span>
                    <p>R$ {valor_multas_mes_atual:,.2f}</p>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="valor_mes"):
                handle_details_display(
                    mes_data,
                    [0, 1, 5, 14],
                    column_map,
                    f"Valor das Multas do Mês {mes_atual:02d}/{ano_atual}"
                )

        # Última Atualização
        with cols[6]:
            data_atualizacao_fmt = data_atualizacao.strftime('%d/%m/%Y') if isinstance(data_atualizacao, (datetime, pd.Timestamp)) else "N/A"
            st.markdown(
                f"""<div class="indicador">
                    <span>Última Atualização</span>
                    <p>{data_atualizacao_fmt}</p>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button("🔍 Detalhes", key="ultima_atualizacao"):
                handle_details_display(
                    unique_fines,
                    [0, 1, 5, 14],
                    column_map,
                    "Última Atualização"
                )

    except Exception as e:
        st.error(f"Erro ao processar os dados: {str(e)}")
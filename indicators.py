import streamlit as st
import pandas as pd
from datetime import datetime

# Configurar a página para usar o layout 'wide'
st.set_page_config(layout="wide")

def handle_table_display(df, columns_to_display, rename_map=None):
    """Função auxiliar para formatar e exibir dataframes"""
    display_df = df[columns_to_display].copy()
    if rename_map:
        display_df = display_df.rename(columns=rename_map)

    # Formatando valores monetários
    if 14 in columns_to_display:
        display_df[rename_map[14]] = display_df[rename_map[14]].apply(lambda x: f'R$ {x:,.2f}')

    # Formatando datas
    if 0 in columns_to_display:
        display_df[rename_map[0]] = pd.to_datetime(display_df[rename_map[0]]).dt.strftime('%d/%m/%Y')

    st.markdown(
        """
        <style>
            [data-testid="stTable"] table {
                width: 100%;
                min-width: 400px;
            }
            [data-testid="stTable"] td {
                white-space: nowrap;
                min-width: 100px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    return st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        height=300
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

    # Definição de colunas para exibição
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

        # Layout dos indicadores
        cols = st.columns(7)
        
        with cols[0]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Total de Multas</span>
                    <p>{total_multas}</p>
                </div>""", 
                unsafe_allow_html=True
            )
            # Mostrar a tabela ao clicar no botão "🔍 Detalhes"
            if st.button("🔍 Detalhes", key="total_multas"):
                handle_table_display(unique_fines, [0, 1, 5], column_map)
                st.download_button(
                    label="Baixar Tabela Completa",
                    data=unique_fines.to_csv(index=False),
                    file_name="multas_total.csv",
                    mime="text/csv"
                )

        with cols[1]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Valor Total das Multas</span>
                    <p>R$ {valor_total_multas:,.2f}</p>
                </div>""",
                unsafe_allow_html=True
            )
            # Mostrar a tabela ao clicar no botão "🔍 Detalhes"
            if st.button("🔍 Detalhes", key="valor_total"):
                handle_table_display(unique_fines, [0, 1, 5, 14], column_map)
                st.download_button(
                    label="Baixar Tabela Completa",
                    data=unique_fines.to_csv(index=False),
                    file_name="multas_valor_total.csv",
                    mime="text/csv"
                )

        with cols[2]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Multas no Ano Atual</span>
                    <p>{multas_ano_atual}</p>
                </div>""",
                unsafe_allow_html=True
            )
            # Mostrar a tabela ao clicar no botão "🔍 Detalhes"
            if st.button("🔍 Detalhes", key="multas_ano"):
                ano_data = unique_fines[unique_fines[9].dt.year == ano_atual]
                handle_table_display(ano_data, [0, 1, 5], column_map)
                st.download_button(
                    label="Baixar Tabela Completa",
                    data=ano_data.to_csv(index=False),
                    file_name="multas_ano_atual.csv",
                    mime="text/csv"
                )

        with cols[3]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Valor Total Multas no Ano Atual</span>
                    <p>R$ {valor_multas_ano_atual:,.2f}</p>
                </div>""",
                unsafe_allow_html=True
            )
            # Mostrar a tabela ao clicar no botão "🔍 Detalhes"
            if st.button("🔍 Detalhes", key="valor_ano"):
                ano_data = unique_fines[unique_fines[9].dt.year == ano_atual]
                handle_table_display(ano_data, [0, 1, 5, 14], column_map)
                st.download_button(
                    label="Baixar Tabela Completa",
                    data=ano_data.to_csv(index=False),
                    file_name="multas_ano_atual_valor.csv",
                    mime="text/csv"
                )

        with cols[4]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Multas no Mês Atual</span>
                    <p>{multas_mes_atual}</p>
                </div>""",
                unsafe_allow_html=True
            )
            # Mostrar a tabela ao clicar no botão "🔍 Detalhes"
            if st.button("🔍 Detalhes", key="multas_mes"):
                mes_data = filtered_data[
                    (filtered_data[9].dt.year == ano_atual) & 
                    (filtered_data[9].dt.month == mes_atual)
                ]
                handle_table_display(mes_data, [0, 1, 5], column_map)
                st.download_button(
                    label="Baixar Tabela Completa",
                    data=mes_data.to_csv(index=False),
                    file_name="multas_mes_atual.csv",
                    mime="text/csv"
                )

        with cols[5]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Valor das Multas no Mês Atual</span>
                    <p>R$ {valor_multas_mes_atual:,.2f}</p>
                </div>""",
                unsafe_allow_html=True
            )
            # Mostrar a tabela ao clicar no botão "🔍 Detalhes"
            if st.button("🔍 Detalhes", key="valor_mes"):
                mes_data = filtered_data[
                    (filtered_data[9].dt.year == ano_atual) & 
                    (filtered_data[9].dt.month == mes_atual)
                ]
                handle_table_display(mes_data, [0, 1, 5, 14], column_map)
                st.download_button(
                    label="Baixar Tabela Completa",
                    data=mes_data.to_csv(index=False),
                    file_name="multas_mes_atual_valor.csv",
                    mime="text/csv"
                )

        with cols[6]:
            st.markdown(
                f"""<div class="indicador">
                    <span>Data da Consulta</span>
                    <p>{data_formatada}</p>
                </div>""",
                unsafe_allow_html=True
            )
            # Exibir informações de período
            st.subheader(f"Período analisado: {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}")

    except Exception as e:
        st.error(f"Erro ao processar os dados: {str(e)}")

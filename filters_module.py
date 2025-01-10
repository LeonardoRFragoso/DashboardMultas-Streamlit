import streamlit as st
import pandas as pd
from datetime import datetime

def apply_filters(data):
    # Estilo para o expander e o aviso de filtro
    st.markdown(
        """
        <style>
            [data-testid="stExpander"] {
                border: 2px solid #F37529;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
                margin-bottom: 20px;
            }
            [data-testid="stExpander"] > summary:hover {
                background-color: rgba(243, 117, 41, 0.1);
                cursor: pointer;
            }
            [data-testid="stExpander"] > summary {
                font-weight: bold;
                font-size: 16px;
                color: #F37529;
                padding: 12px;
            }
            .filtro-alerta {
                text-align: center;
                color: #F37529;
                background-color: rgba(243, 117, 41, 0.05);
                padding: 8px;
                border-radius: 8px;
                font-size: 14px;
                margin: 15px 0;
                font-weight: 500;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Alerta sutil para indicar que os filtros estão disponíveis
    st.markdown('<div class="filtro-alerta">🔍 Utilize os filtros abaixo para refinar os resultados de forma mais precisa.</div>', unsafe_allow_html=True)

    with st.expander("🔧 Filtros para Refinamento de Dados", expanded=False):
        st.markdown('<p class="filtro-alerta">Ajuste os filtros para uma análise detalhada das multas.</p>', unsafe_allow_html=True)
        
        data_inicio = st.date_input("Data de Início", value=datetime(2024, 1, 1))
        data_fim = st.date_input("Data Final", value=datetime(datetime.now().year, 12, 31))
        
        codigo_infracao_opcoes = data[8].dropna().unique()
        codigo_infracao_selecionado = st.multiselect(
            "Selecione o Código da Infração",
            options=codigo_infracao_opcoes,
            default=codigo_infracao_opcoes.tolist()
        )

        descricao_infracao_opcoes = data[11].dropna().unique()
        descricao_infracao_selecionada = st.multiselect(
            "Selecione a Descrição da Infração",
            options=descricao_infracao_opcoes,
            default=descricao_infracao_opcoes.tolist()
        )

        valor_min, valor_max = st.slider(
            "Selecione o intervalo de valores das multas",
            min_value=float(data[14].min()),
            max_value=float(data[14].max()),
            value=(float(data[14].min()), float(data[14].max())),
            step=0.01
        )

        placa_opcoes = data[1].dropna().unique()
        placa_selecionada = st.multiselect(
            "Selecione a Placa do Veículo",
            options=placa_opcoes,
            default=placa_opcoes.tolist()
        )

        # Verificação para evitar dataframe vazio
        if not placa_selecionada:
            st.warning("Nenhuma placa selecionada. Exibindo todos os dados.")
            placa_selecionada = placa_opcoes

    filtered_data = data[
        (data[9] >= pd.Timestamp(data_inicio)) &
        (data[9] <= pd.Timestamp(data_fim)) &
        (data[8].isin(codigo_infracao_selecionado)) &
        (data[11].isin(descricao_infracao_selecionada)) &
        (data[14] >= valor_min) &
        (data[14] <= valor_max) &
        (data[1].isin(placa_selecionada))
    ]

    # Retornar os dados filtrados + as datas selecionadas
    return filtered_data, data_inicio, data_fim

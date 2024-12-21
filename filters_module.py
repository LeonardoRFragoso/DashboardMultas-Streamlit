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
            }
            [data-testid="stExpander"] > summary {
                font-weight: bold;
                font-size: 16px;
                color: #F37529;
            }
            .filtro-alerta {
                text-align: center;
                color: #F37529;
                font-size: 14px;
                margin-bottom: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Alerta sutil para indicar que os filtros estão disponíveis
    st.markdown('<div class="filtro-alerta">🔍 Use os filtros abaixo para refinar os resultados.</div>', unsafe_allow_html=True)

    with st.expander("🔧 Filtros para Refinamento de Dados", expanded=False):
        data_inicio = st.date_input("Data de Início", value=datetime(datetime.now().year, 1, 1))
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

import streamlit as st
import pandas as pd
from datetime import datetime

def apply_filters(data):
    with st.expander("Filtros", expanded=True):
        data_inicio = st.date_input("Data de Início", value=datetime(datetime.now().year, 1, 1))
        data_fim = st.date_input("Data Final", value=datetime(datetime.now().year, 12, 31))
        
        # Multiselect para código de infração
        codigo_infracao_opcoes = data[8].dropna().unique()
        codigo_infracao_selecionado = st.multiselect(
            "Selecione o Código da Infração",
            options=codigo_infracao_opcoes,
            default=codigo_infracao_opcoes.tolist()
        )

        # Multiselect para descrição da infração
        descricao_infracao_opcoes = data[11].dropna().unique()
        descricao_infracao_selecionada = st.multiselect(
            "Selecione a Descrição da Infração",
            options=descricao_infracao_opcoes,
            default=descricao_infracao_opcoes.tolist()
        )

        # Filtro de valores
        valor_min, valor_max = st.slider(
            "Selecione o intervalo de valores das multas",
            min_value=float(data[14].min()),
            max_value=float(data[14].max()),
            value=(float(data[14].min()), float(data[14].max())),
            step=0.01
        )

        # Multiselect para placa do veículo
        placa_opcoes = data[1].dropna().unique()
        placa_selecionada = st.multiselect(
            "Selecione a Placa do Veículo",
            options=placa_opcoes,
            default=placa_opcoes.tolist()
        )

    # Aplicar filtros ao dataframe
    filtered_data = data[
        (data[9] >= pd.Timestamp(data_inicio)) &
        (data[9] <= pd.Timestamp(data_fim)) &
        (data[8].isin(codigo_infracao_selecionado)) &
        (data[11].isin(descricao_infracao_selecionada)) &
        (data[14] >= valor_min) &
        (data[14] <= valor_max) &
        (data[1].isin(placa_selecionada))
    ]
    
    return filtered_data

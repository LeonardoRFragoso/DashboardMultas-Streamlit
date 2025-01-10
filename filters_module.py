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
        
        # Encontrar a data mais antiga e mais recente nos dados
        min_date = pd.to_datetime(data[9]).min()
        max_date = pd.to_datetime(data[9]).max()
        
        if pd.isna(min_date):
            min_date = datetime(2017, 1, 1)
        if pd.isna(max_date):
            max_date = datetime.now()
            
        # Debug - mostrar datas encontradas
        st.write("Data mais antiga:", min_date)
        st.write("Data mais recente:", max_date)
        
        data_inicio = st.date_input("Data de Início", value=min_date)
        data_fim = st.date_input("Data Final", value=max_date)
        
        codigo_infracao_opcoes = data[8].dropna().unique()
        if len(codigo_infracao_opcoes) > 0:
            codigo_infracao = st.multiselect("Código da Infração", options=sorted(codigo_infracao_opcoes))
        
        placa_opcoes = data[2].dropna().unique()
        if len(placa_opcoes) > 0:
            placa = st.multiselect("Placa do Veículo", options=sorted(placa_opcoes))
        
        # Aplicar filtros
        filtered_data = data.copy()
        
        # Filtro de data
        filtered_data[9] = pd.to_datetime(filtered_data[9])
        filtered_data = filtered_data[
            (filtered_data[9].dt.date >= data_inicio) & 
            (filtered_data[9].dt.date <= data_fim)
        ]
        
        # Filtro de código de infração
        if codigo_infracao:
            filtered_data = filtered_data[filtered_data[8].isin(codigo_infracao)]
            
        # Filtro de placa
        if placa:
            filtered_data = filtered_data[filtered_data[2].isin(placa)]
            
        # Debug - mostrar contagem após filtros
        st.write("Total de registros após filtros:", len(filtered_data))
        st.write("Anos únicos após filtros:", sorted(filtered_data[9].dt.year.unique()))
        
        return filtered_data
        
    return data

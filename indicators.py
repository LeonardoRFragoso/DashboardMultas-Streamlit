import streamlit as st
import pandas as pd
from datetime import datetime

# Função para aplicar o CSS correto
def render_css():
    st.markdown(
        """
        <style>
            .indicadores-container {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 30px;
                flex-wrap: wrap;
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
                cursor: pointer;
                transition: transform 0.2s ease-in-out;
            }
            .indicador:hover {
                transform: scale(1.05);
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
            .hidden {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Função para calcular e exibir indicadores principais
def render_indicators(data, filtered_data, data_inicio, data_fim):
    render_css()

    # Calcular indicadores principais
    if 5 in data.columns:
        unique_fines = data.drop_duplicates(subset=[5])
    else:
        st.error("A coluna com índice 5 não foi encontrada nos dados.")
        unique_fines = pd.DataFrame(columns=[5, 14, 9])

    if 'filtro_aplicado' not in st.session_state:
        st.session_state['filtro_aplicado'] = False

    if not st.session_state['filtro_aplicado']:
        total_multas = unique_fines[5].nunique() if 5 in unique_fines.columns else 0
        valor_total_multas = unique_fines[14].sum() if 14 in unique_fines.columns else 0
        filtered_unique_fines = unique_fines
    else:
        if data_inicio == datetime(datetime.now().year, 1, 1).date() and data_fim == datetime.now().date():
            total_multas = unique_fines[5].nunique()
            valor_total_multas = unique_fines[14].sum()
            filtered_unique_fines = unique_fines
        else:
            if filtered_data.empty:
                total_multas = 0
                valor_total_multas = 0
                filtered_unique_fines = pd.DataFrame(columns=[5, 14, 9])
            else:
                filtered_unique_fines = filtered_data.drop_duplicates(subset=[5])
                total_multas = filtered_unique_fines[5].nunique()
                valor_total_multas = filtered_unique_fines[14].sum()

    ano_atual = datetime.now().year
    mes_atual = data_fim.month if data_fim else datetime.now().month

    multas_ano_atual = filtered_data[filtered_data[9].dt.year == ano_atual][5].nunique() if 9 in filtered_data.columns else 0
    valor_multas_ano_atual = filtered_data[filtered_data[9].dt.year == ano_atual][14].sum() if 14 in filtered_data.columns else 0

    multas_mes_atual = filtered_data[
        (filtered_data[9].dt.year == ano_atual) & (filtered_data[9].dt.month == mes_atual)
    ][5].nunique() if 9 in filtered_data.columns else 0
    valor_multas_mes_atual = filtered_data[
        (filtered_data[9].dt.year == ano_atual) & (filtered_data[9].dt.month == mes_atual)
    ][14].sum() if 14 in filtered_data.columns else 0

    # Exibir indicadores lado a lado como cards clicáveis
    st.markdown('<div class="indicadores-container">', unsafe_allow_html=True)

    def create_card(title, value, key):
        card_html = f"""
        <div class="indicador" onclick="toggleVisibility('{key}')">
            <span>{title}</span>
            <p>{value}</p>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

    create_card("Total de Multas", total_multas, "total_multas")
    create_card("Valor Total das Multas", f"R$ {valor_total_multas:,.2f}", "valor_total")
    create_card("Multas no Ano Atual", multas_ano_atual, "multas_ano")
    create_card("Valor Total Multas no Ano Atual", f"R$ {valor_multas_ano_atual:,.2f}", "valor_ano")
    create_card("Multas no Mês Atual", multas_mes_atual, "multas_mes")
    create_card("Valor das Multas no Mês Atual", f"R$ {valor_multas_mes_atual:,.2f}", "valor_mes")

    st.markdown('</div>', unsafe_allow_html=True)

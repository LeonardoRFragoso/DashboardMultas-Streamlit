import streamlit as st
import pandas as pd
from datetime import datetime

# Função para aplicar o CSS original
def render_css():
    st.markdown(
        """
        <style>
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

    # Inicialização do filtro
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

    # Exibir indicadores como cards clicáveis
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Total de Multas", key="total_multas_button"):
                st.session_state["show_total_multas"] = not st.session_state.get("show_total_multas", False)
            st.markdown(
                f"""
                <div class="indicador">
                    <span>Total de Multas</span>
                    <p>{total_multas}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""
                <div class="indicador">
                    <span>Valor Total das Multas</span>
                    <p>R$ {valor_total_multas:,.2f}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Detalhes ocultos que aparecem ao clicar
    if st.session_state.get("show_total_multas", False):
        with st.expander("Detalhes do Total de Multas", expanded=True):
            st.dataframe(
                filtered_unique_fines[[1, 12, 14, 9]].rename(
                    columns={
                        1: 'Placa Relacionada',
                        12: 'Local da Infração',
                        14: 'Valor a ser pago R$',
                        9: 'Data da Infração'
                    }
                ).reset_index(drop=True),
                use_container_width=True,
            )

import streamlit as st
import pandas as pd
from datetime import datetime

# Aplica o CSS diretamente aos cards
def render_css():
    st.markdown(
        """
        <style>
            .indicadores-container {
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 20px;
                margin-top: 30px;
            }
            .indicador {
                background-color: #FFFFFF;
                border: 4px solid #0066B4;
                border-radius: 15px;
                box-shadow: 0 8px 12px rgba(0, 0, 0, 0.3);
                text-align: center;
                padding: 20px;
                cursor: pointer;
                transition: transform 0.2s ease-in-out;
                width: 180px;
                height: 130px;
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
        </style>
        """,
        unsafe_allow_html=True,
    )

# Renderiza os indicadores principais
def render_indicators(data, filtered_data, data_inicio, data_fim):
    render_css()

    # Calcula indicadores
    total_multas = data[5].nunique() if 5 in data.columns else 0
    valor_total_multas = data[14].sum() if 14 in data.columns else 0
    ano_atual = datetime.now().year
    multas_ano_atual = filtered_data[filtered_data[9].dt.year == ano_atual][5].nunique() if 9 in filtered_data.columns else 0
    valor_multas_ano_atual = filtered_data[filtered_data[9].dt.year == ano_atual][14].sum() if 14 in filtered_data.columns else 0
    multas_mes_atual = filtered_data[(filtered_data[9].dt.year == ano_atual) & (filtered_data[9].dt.month == datetime.now().month)][5].nunique() if 9 in filtered_data.columns else 0
    valor_multas_mes_atual = filtered_data[(filtered_data[9].dt.year == ano_atual) & (filtered_data[9].dt.month == datetime.now().month)][14].sum() if 14 in filtered_data.columns else 0
    
    try:
        data_consulta = data.iloc[1, 0]  # Segunda linha (linha 2)
        data_formatada = data_consulta.strftime('%d/%m/%Y') if isinstance(data_consulta, pd.Timestamp) else str(data_consulta)
    except:
        data_formatada = "N/A"

    # Cria dicionário para armazenar os valores
    indicadores = {
        "Total Multas": total_multas,
        "Valor Total": f"R$ {valor_total_multas:,.2f}",
        "Multas Ano": multas_ano_atual,
        "Valor Ano": f"R$ {valor_multas_ano_atual:,.2f}",
        "Multas Mes": multas_mes_atual,
        "Valor Mes": f"R$ {valor_multas_mes_atual:,.2f}",
        "Data Consulta": data_formatada
    }

    # Inicializa o estado de clique
    if 'selected_indicator' not in st.session_state:
        st.session_state.selected_indicator = None

    # Cria os cards usando colunas
    cols = st.columns(7)  # 7 Colunas para garantir o alinhamento horizontal
    indicadores_keys = list(indicadores.keys())
    
    for i, col in enumerate(cols):
        with col:
            # Renderiza o card diretamente clicável
            if st.button(indicadores_keys[i]):
                if st.session_state.selected_indicator == indicadores_keys[i]:
                    st.session_state.selected_indicator = None
                else:
                    st.session_state.selected_indicator = indicadores_keys[i]
            
            # Renderiza visual do card
            st.markdown(
                f"""
                <div class="indicador">
                    <span>{indicadores_keys[i]}</span>
                    <p>{indicadores[indicadores_keys[i]]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Exibe tabela se um indicador for clicado duas vezes
    if st.session_state.selected_indicator:
        exibir_tabela(st.session_state.selected_indicator, data, filtered_data)

# Função para exibir tabela com base no card clicado
def exibir_tabela(indicador_id, data, filtered_data):
    st.markdown(f"### Detalhes: {indicador_id}")
    
    if indicador_id == "Total Multas":
        tabela = data.drop_duplicates(subset=[5])  # Exibe todas as multas únicas
    elif indicador_id == "Valor Total":
        tabela = data[[5, 14, 12, 9]].drop_duplicates(subset=[5])  # Valor por infração
    elif indicador_id == "Multas Ano":
        tabela = filtered_data[filtered_data[9].dt.year == datetime.now().year]
    elif indicador_id == "Valor Ano":
        tabela = filtered_data[filtered_data[9].dt.year == datetime.now().year]
    elif indicador_id == "Multas Mes":
        tabela = filtered_data[
            (filtered_data[9].dt.year == datetime.now().year) & 
            (filtered_data[9].dt.month == datetime.now().month)
        ]
    elif indicador_id == "Valor Mes":
        tabela = filtered_data[
            (filtered_data[9].dt.year == datetime.now().year) & 
            (filtered_data[9].dt.month == datetime.now().month)
        ]
    else:
        tabela = pd.DataFrame(columns=["Nenhum dado encontrado."])

    st.dataframe(tabela.reset_index(drop=True))

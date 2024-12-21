import streamlit as st
import pandas as pd
from datetime import datetime

# Função para aplicar o CSS
def render_css():
    st.markdown(
        """
        <style>
            .indicadores-container {
                display: grid;
                grid-template-columns: repeat(7, 1fr);
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
                width: 210px;
                height: 140px;
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
                font-size: 24px;
                color: #0066B4;
                margin: 0;
                font-weight: bold;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Função para exibir a tabela ao clicar no indicador
def exibir_tabela(indicador_id, data, filtered_data):
    st.markdown(f"### Detalhes: {indicador_id.replace('_', ' ').title()}")

    if indicador_id == "total_multas":
        tabela = data.drop_duplicates(subset=[5])
    elif indicador_id == "valor_total":
        tabela = data[[5, 14, 12, 9]].drop_duplicates(subset=[5])
    elif indicador_id == "multas_ano":
        tabela = filtered_data[filtered_data[9].dt.year == datetime.now().year]
    elif indicador_id == "valor_ano":
        tabela = filtered_data[filtered_data[9].dt.year == datetime.now().year]
    elif indicador_id == "multas_mes":
        tabela = filtered_data[
            (filtered_data[9].dt.year == datetime.now().year) & 
            (filtered_data[9].dt.month == datetime.now().month)
        ]
    elif indicador_id == "valor_mes":
        tabela = filtered_data[
            (filtered_data[9].dt.year == datetime.now().year) & 
            (filtered_data[9].dt.month == datetime.now().month)
        ]
    else:
        tabela = pd.DataFrame(columns=["Nenhum dado encontrado."])

    st.dataframe(tabela.reset_index(drop=True))

# Função para renderizar indicadores
def render_indicators(data, filtered_data, data_inicio, data_fim):
    render_css()

    if 5 in data.columns:
        unique_fines = data.drop_duplicates(subset=[5])
    else:
        st.error("A coluna com índice 5 não foi encontrada nos dados.")
        unique_fines = pd.DataFrame(columns=[5, 14, 9])

    # Cálculos dos indicadores
    total_multas = unique_fines[5].nunique() if 5 in unique_fines.columns else 0
    valor_total_multas = unique_fines[14].sum() if 14 in unique_fines.columns else 0
    ano_atual = datetime.now().year
    mes_atual = data_fim.month if data_fim else datetime.now().month

    multas_ano_atual = unique_fines[unique_fines[9].dt.year == ano_atual][5].nunique() if 9 in unique_fines.columns else 0
    valor_multas_ano_atual = unique_fines[unique_fines[9].dt.year == ano_atual][14].sum() if 14 in unique_fines.columns else 0

    multas_mes_atual = filtered_data[
        (filtered_data[9].dt.year == ano_atual) & (filtered_data[9].dt.month == mes_atual)
    ][5].nunique() if 9 in filtered_data.columns else 0

    valor_multas_mes_atual = filtered_data[
        (filtered_data[9].dt.year == ano_atual) & (filtered_data[9].dt.month == mes_atual)
    ][14].sum() if 14 in filtered_data.columns else 0

    try:
        data_consulta = data.iloc[1, 0]
        data_formatada = (
            data_consulta.strftime('%d/%m/%Y')
            if isinstance(data_consulta, pd.Timestamp) else str(data_consulta)
        )
    except (IndexError, KeyError):
        data_formatada = "N/A"

    # Inicializa o estado de clique
    if 'selected_indicator' not in st.session_state:
        st.session_state.selected_indicator = None

    # Renderizar os indicadores
    indicadores = {
        "total_multas": total_multas,
        "valor_total": f"R$ {valor_total_multas:,.2f}",
        "multas_ano": multas_ano_atual,
        "valor_ano": f"R$ {valor_multas_ano_atual:,.2f}",
        "multas_mes": multas_mes_atual,
        "valor_mes": f"R$ {valor_multas_mes_atual:,.2f}",
        "data_consulta": data_formatada
    }

    indicadores_keys = list(indicadores.keys())

    # Renderizar como HTML clicável
    indicadores_html = '<div class="indicadores-container">'
    
    for i in indicadores_keys:
        indicadores_html += f"""
        <div class="indicador" onclick="send('{i}')">
            <span>{i.replace('_', ' ').title()}</span>
            <p>{indicadores[i]}</p>
        </div>
        """
    indicadores_html += '</div>'

    st.markdown(indicadores_html, unsafe_allow_html=True)

    # JavaScript para capturar o clique e atualizar o estado
    st.markdown(
        """
        <script>
        function send(value) {{
            var indicator = value;
            var url = window.location.href + "?indicator=" + indicator;
            fetch(url);
            window.location.reload();
        }}
        </script>
        """,
        unsafe_allow_html=True,
    )

    # Captura o parâmetro do clique e exibe a tabela
    query_params = st.experimental_get_query_params()
    if "indicator" in query_params:
        selected = query_params["indicator"][0]
        st.session_state.selected_indicator = selected
        exibir_tabela(selected, data, filtered_data)

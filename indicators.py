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
            .selected {
                border: 4px solid red !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

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

    # Inicializa o estado de clique duplo
    if 'clicked_indicator' not in st.session_state:
        st.session_state.clicked_indicator = None
        st.session_state.click_count = 0

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

    # Renderizar HTML interativo com duplo clique
    indicadores_html = "<div class='indicadores-container'>"
    for key, value in indicadores.items():
        selected_class = "selected" if st.session_state.clicked_indicator == key else ""
        indicadores_html += f"""
        <div class="indicador {selected_class}" ondblclick="send('{key}')">
            <span>{key.replace('_', ' ').title()}</span>
            <p>{value}</p>
        </div>
        """
    indicadores_html += "</div>"

    # Javascript para manipular duplo clique e enviar para Streamlit
    indicadores_html += """
    <script>
        function send(indicator) {{
            const query = new URLSearchParams(window.location.search);
            query.set('clicked_indicator', indicator);
            window.location.search = query.toString();
        }}
    </script>
    """

    # Renderizar HTML no Streamlit
    st.markdown(indicadores_html, unsafe_allow_html=True)

    # Captura o parâmetro de URL para simular clique duplo
    clicked_indicator = st.experimental_get_query_params().get("clicked_indicator", [None])[0]

    if clicked_indicator:
        st.session_state.clicked_indicator = clicked_indicator
        st.session_state.click_count += 1

    # Exibe tabela ao clicar duas vezes
    if st.session_state.click_count >= 2:
        exibir_tabela(st.session_state.clicked_indicator, data, filtered_data)
        st.session_state.click_count = 0

# Função para exibir tabela ao clicar duas vezes
def exibir_tabela(indicador_id, data, filtered_data):
    st.markdown(f"### Detalhes: {indicador_id.replace('_', ' ').title()}")

    if indicador_id == "total_multas":
        tabela = data.drop_duplicates(subset=[5])
    elif indicador_id == "valor_total":
        tabela = data[[5, 14, 12, 9]].drop_duplicates(subset=[5])
    else:
        tabela = filtered_data

    st.dataframe(tabela.reset_index(drop=True))

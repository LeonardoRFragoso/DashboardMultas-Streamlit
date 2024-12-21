import streamlit as st
import pandas as pd
from datetime import datetime

# Função para aplicar o CSS dos indicadores
def render_css():
    st.markdown(
        """
        <style>
            .indicadores-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                justify-content: center;
                gap: 20px;
                margin-top: 30px;
                max-width: 1400px;
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
                cursor: pointer;
                transition: transform 0.2s ease-in-out;
                width: 190px;
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

# Função para renderizar os indicadores principais
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
        "total_multas": total_multas,
        "valor_total": f"R$ {valor_total_multas:,.2f}",
        "multas_ano": multas_ano_atual,
        "valor_ano": f"R$ {valor_multas_ano_atual:,.2f}",
        "multas_mes": multas_mes_atual,
        "valor_mes": f"R$ {valor_multas_mes_atual:,.2f}",
        "data_consulta": data_formatada
    }

    # Inicializa o estado para rastrear cliques duplos
    if 'selected_indicator' not in st.session_state:
        st.session_state.selected_indicator = None

    # Renderiza Indicadores
    indicadores_keys = list(indicadores.keys())

    st.markdown('<div class="indicadores-container">', unsafe_allow_html=True)
    for indicador in indicadores_keys:
        # Cada card é um botão invisível que executa o clique duplo
        js_code = f"""
        <script>
        var card = document.getElementById('{indicador}');
        card.addEventListener('dblclick', function() {{
            fetch('/_stcore/double_click?indicador={indicador}').then(r => r.json()).then(data => {{
                var el = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                el.scrollTop = el.scrollHeight;
            }});
        }});
        </script>
        """

        # Renderiza cada card com um ID único para capturar o evento de clique duplo
        st.markdown(
            f"""
            <div class="indicador" id="{indicador}">
                <span>{indicador.replace('_', ' ').title()}</span>
                <p>{indicadores[indicador]}</p>
            </div>
            {js_code}
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Exibe tabela se um indicador for clicado duas vezes
    if st.query_params.get("indicador"):
        exibir_tabela(st.query_params["indicador"], data, filtered_data)

# Função para exibir tabela ao clicar duas vezes em um indicador
def exibir_tabela(indicador_id, data, filtered_data):
    st.markdown(f"### Detalhes: {indicador_id.replace('_', ' ').title()}")
    
    if indicador_id == "total_multas":
        tabela = data.drop_duplicates(subset=[5])  # Exibe todas as multas únicas
    elif indicador_id == "valor_total":
        tabela = data[[5, 14, 12, 9]].drop_duplicates(subset=[5])  # Mostra valor por infração
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

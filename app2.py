import streamlit as st
import pandas as pd
from datetime import datetime

def load_data():
    try:
        data = pd.read_excel('ResultadosOrganizados.xlsx')
        if 9 in data.columns:
            data[9] = pd.to_datetime(data[9], errors='coerce')
        return data
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def filter_data(data, data_inicio=None, data_fim=None):
    filtered_data = data.copy()
    if data_inicio and data_fim and 9 in filtered_data.columns:
        try:
            filtered_data = filtered_data[
                (filtered_data[9].notna()) & 
                (filtered_data[9] >= pd.to_datetime(data_inicio)) & 
                (filtered_data[9] <= pd.to_datetime(data_fim))
            ]
        except Exception as e:
            st.error(f"Erro ao filtrar dados por data: {e}")
    return filtered_data

def render_css():
    st.markdown("""
        <style>
            .indicadores-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
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

            .stButton > button {
                background-color: #F37529 !important;
                color: white !important;
                font-weight: 600 !important;
                padding: 10px 24px !important;
                border: none !important;
                border-radius: 8px !important;
                width: 100% !important;
                font-size: 15px !important;
                letter-spacing: 0.5px !important;
                box-shadow: 0 4px 12px rgba(243, 117, 41, 0.2) !important;
                margin-top: 10px !important;
            }
            
            .stButton > button:hover {
                background-color: #ff8c42 !important;
                transform: translateY(-2px) !important;
                transition: all 0.2s ease !important;
                box-shadow: 0 6px 16px rgba(243, 117, 41, 0.3) !important;
            }

            .indicador-wrapper {
                margin-bottom: 20px;
            }

            .main-title {
                text-align: center;
                padding: 20px;
                background: #F37529;
                color: white;
                border-radius: 10px;
                margin-bottom: 20px;
            }

            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
            }

            .dica {
                text-align: center;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 5px;
                margin: 20px 0;
            }
        </style>
    """, unsafe_allow_html=True)

def render_indicator(title, value, key):
    st.markdown(f"""
        <div class="indicador-wrapper">
            <div class="indicador">
                <span>{title}</span>
                <p>{value}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 Detalhes", key=f"details_{key}", 
                type="primary",
                help=f"Clique para ver os detalhes de {title}"):
        st.session_state[f'show_details_{key}'] = not st.session_state.get(f'show_details_{key}', False)

def main():
    st.set_page_config(page_title="Dashboard de Multas", layout="wide", initial_sidebar_state="collapsed")
    render_css()

    st.markdown('<h1 class="main-title">TORRE DE CONTROLE ITRACKER - DASHBOARD DE MULTAS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Monitorando em tempo real as consultas de multas no DETRAN-RJ</p>', unsafe_allow_html=True)

    # Carrega dados
    data = load_data()
    
    # Filtros de data
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Inicial", datetime.now())
    with col2:
        data_fim = st.date_input("Data Final", datetime.now())

    filtered_data = filter_data(data, data_inicio, data_fim)
    
    st.markdown('<p class="dica">🔍 Utilize os filtros acima para refinar os resultados de forma mais precisa.</p>', unsafe_allow_html=True)

    try:
        # Cálculos dos indicadores
        unique_fines = filtered_data.drop_duplicates(subset=[5]) if 5 in filtered_data.columns else pd.DataFrame()
        
        total_multas = len(unique_fines) if not unique_fines.empty else 0
        valor_total_multas = unique_fines[14].sum() if (14 in unique_fines.columns and not unique_fines.empty) else 0
        
        ano_atual = datetime.now().year
        mes_atual = datetime.now().month
        
        if 9 in unique_fines.columns and not unique_fines.empty:
            unique_fines[9] = pd.to_datetime(unique_fines[9], errors='coerce')
            multas_ano_atual = len(unique_fines[unique_fines[9].dt.year == ano_atual])
            valor_multas_ano_atual = unique_fines[unique_fines[9].dt.year == ano_atual][14].sum() if 14 in unique_fines.columns else 0
            
            multas_mes_atual = len(unique_fines[
                (unique_fines[9].dt.year == ano_atual) & 
                (unique_fines[9].dt.month == mes_atual)
            ])
            
            valor_multas_mes_atual = unique_fines[
                (unique_fines[9].dt.year == ano_atual) & 
                (unique_fines[9].dt.month == mes_atual)
            ][14].sum() if 14 in unique_fines.columns else 0
        else:
            multas_ano_atual = 0
            valor_multas_ano_atual = 0
            multas_mes_atual = 0
            valor_multas_mes_atual = 0

        # Grid layout com colunas para os indicadores
        col1, col2, col3, col4 = st.columns(4)
        col5, col6, col7 = st.columns(3)

        with col1:
            render_indicator("Total de Multas", total_multas, "total_multas")
            if st.session_state.get('show_details_total_multas', False):
                st.dataframe(unique_fines)

        with col2:
            render_indicator("Valor Total das Multas", f"R$ {valor_total_multas:,.2f}", "valor_total")
            if st.session_state.get('show_details_valor_total', False):
                st.dataframe(unique_fines[[5, 14]] if not unique_fines.empty else pd.DataFrame())

        with col3:
            render_indicator("Multas no Ano Atual", multas_ano_atual, "multas_ano")
            if st.session_state.get('show_details_multas_ano', False):
                st.dataframe(unique_fines[unique_fines[9].dt.year == ano_atual] if not unique_fines.empty else pd.DataFrame())

        with col4:
            render_indicator("Valor Total Multas no Ano Atual", f"R$ {valor_multas_ano_atual:,.2f}", "valor_ano")
            if st.session_state.get('show_details_valor_ano', False):
                st.dataframe(unique_fines[unique_fines[9].dt.year == ano_atual][[5, 14]] if not unique_fines.empty else pd.DataFrame())

        with col5:
            render_indicator("Multas no Mês Atual", multas_mes_atual, "multas_mes")
            if st.session_state.get('show_details_multas_mes', False):
                st.dataframe(unique_fines[
                    (unique_fines[9].dt.year == ano_atual) & 
                    (unique_fines[9].dt.month == mes_atual)
                ] if not unique_fines.empty else pd.DataFrame())

        with col6:
            render_indicator("Valor das Multas no Mês Atual", f"R$ {valor_multas_mes_atual:,.2f}", "valor_mes")
            if st.session_state.get('show_details_valor_mes', False):
                st.dataframe(unique_fines[
                    (unique_fines[9].dt.year == ano_atual) & 
                    (unique_fines[9].dt.month == mes_atual)
                ][[5, 14]] if not unique_fines.empty else pd.DataFrame())

        with col7:
            render_indicator("Data da Consulta", data_inicio.strftime('%d/%m/%Y'), "data_consulta")
            if st.session_state.get('show_details_data_consulta', False):
                st.write(f"Período: {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}")

    except Exception as e:
        st.error(f"Erro ao processar os dados: {e}")

if __name__ == "__main__":
    main()
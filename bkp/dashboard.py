import streamlit as st
from data_loader import carregar_planilha
from data_processor import processar_dados

# Importações adicionais para gráficos
from graph_common_infractions import create_common_infractions_chart
from graph_weekday_infractions import create_weekday_infractions_chart
from graph_fines_accumulated import create_fines_accumulated_chart
from graph_geo_distribution import create_geo_distribution_map
from graph_vehicles_fines import create_vehicle_fines_chart


def render_dashboard(file_id, drive_service):
    """
    Renderiza o dashboard de multas.

    Args:
        file_id (str): ID do arquivo no Google Drive.
        drive_service (googleapiclient.discovery.Resource): Serviço do Google Drive.
    """
    # CSS personalizado
    st.markdown(
        """
        <style>
        .main-container {
            padding: 0;
        }
        .logo-container {
            text-align: center;
            margin-bottom: 20px;
        }
        .title-container {
            background: linear-gradient(90deg, #F37529, #FFDDC1);
            color: white;
            text-align: center;
            padding: 15px 0;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .indicadores-container {
            display: flex;
            justify-content: space-around;
            text-align: center;
            margin-bottom: 40px;
        }
        .indicador {
            background: #FFFFFF;
            padding: 20px 40px;
            border-radius: 12px;
            border: 2px solid #F37529;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .indicador:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }
        .footer {
            margin-top: 50px;
            text-align: center;
            font-size: 14px;
            color: #888;
            padding: 10px;
            background-color: #f9f9f9;
            border-top: 1px solid #eee;
        }
        .titulo-centralizado {
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: #F37529;
            margin-top: 40px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Exibir logo
    logo_url = st.secrets["image"]["logo_url"]
    st.markdown(
        f"""
        <div class="logo-container">
            <img src="{logo_url}" alt="Logo" width="150">
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Título do dashboard
    st.markdown(
        """
        <div class="title-container">
            <h1>Torre de Controle - Dashboard de Multas</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Carregar dados
    st.markdown("<h1>Carregando os dados...</h1>", unsafe_allow_html=True)
    try:
        df = carregar_planilha(file_id, drive_service)
        st.success("Dados carregados com sucesso!")
    except Exception as e:
        st.error(f"Erro ao carregar os dados. Verifique as credenciais e o ID do arquivo: {e}")
        st.stop()

    # Processar dados
    try:
        df_ultimo_dia, ultimo_dia = processar_dados(df)
    except Exception as e:
        st.error(f"Erro ao processar os dados: {e}")
        st.stop()

    # Indicadores principais
    try:
        num_registros_unicos = len(df_ultimo_dia)
        valor_total_ultimo_dia = df_ultimo_dia["Valor Calculado"].sum()

        st.markdown(
            f"""
            <div class="indicadores-container">
                <div class="indicador">
                    <h3>Total de Registros Únicos</h3>
                    <p>{num_registros_unicos}</p>
                </div>
                <div class="indicador">
                    <h3>Valor Total a Pagar</h3>
                    <p>R$ {valor_total_ultimo_dia:,.2f}</p>
                </div>
                <div class="indicador">
                    <h3>Última Consulta</h3>
                    <p>{ultimo_dia.strftime('%d/%m/%Y')}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.error(f"Erro ao exibir os indicadores principais: {e}")

    # Exibir gráficos no dashboard
    try:
        st.markdown("<h2 class='titulo-centralizado'>Top 10 Veículos com Mais Multas e Valores Totais</h2>", unsafe_allow_html=True)
        st.plotly_chart(create_vehicle_fines_chart(df_ultimo_dia), use_container_width=True)

        st.markdown("<h2 class='titulo-centralizado'>Infrações Mais Frequentes</h2>", unsafe_allow_html=True)
        st.plotly_chart(create_common_infractions_chart(df_ultimo_dia), use_container_width=True)

        st.markdown("<h2 class='titulo-centralizado'>Distribuição Geográfica das Multas</h2>", unsafe_allow_html=True)
        create_geo_distribution_map(df_ultimo_dia, st.secrets["API_KEY"])

        st.markdown("<h2 class='titulo-centralizado'>Valores das Multas Acumulados por Período</h2>", unsafe_allow_html=True)
        st.plotly_chart(create_fines_accumulated_chart(df_ultimo_dia), use_container_width=True)

        st.markdown("<h2 class='titulo-centralizado'>Infrações Mais Frequentes por Dia da Semana</h2>", unsafe_allow_html=True)
        st.plotly_chart(create_weekday_infractions_chart(df_ultimo_dia), use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao exibir os gráficos: {e}")

    # Rodapé
    st.markdown(
        """
        <div class="footer">
            Dashboard de Multas © 2024 | Desenvolvido pela Equipe de Qualidade
        </div>
        """,
        unsafe_allow_html=True,
    )

import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

def create_monthly_fines_chart(data):
    """
    Cria gráfico de linhas para multas mensais com seletor de ano.
    """
    # Converter coluna de data e remover valores nulos
    data = data.copy()  # Criar uma cópia para evitar SettingWithCopyWarning
    data[9] = pd.to_datetime(data[9], errors='coerce')
    
    # Filtrar apenas registros que têm multas
    data = data[data[5].notna()]
    data = data.dropna(subset=[9])

    # Remover duplicatas baseado no Auto de Infração
    data = data.drop_duplicates(subset=[5])

    # Converter valores monetários
    data[14] = (data[14].astype(str)
                .str.replace(r'[^\d,.-]', '', regex=True)
                .str.replace(',', '.')
                .astype(float))

    # Forçar o range de anos de 2017 até o próximo ano
    min_ano = 2017
    max_ano = datetime.now().year + 1
    anos_disponiveis = list(range(min_ano, max_ano + 1))
    
    if not anos_disponiveis:
        st.warning("Não há dados disponíveis para exibir o gráfico mensal.")
        return None

    # Criar seletor de ano
    col1, col2 = st.columns([2, 8])
    with col1:
        selected_year = st.selectbox(
            "Selecione o Ano",
            anos_disponiveis,
            index=anos_disponiveis.index(datetime.now().year)  # Seleciona o ano atual por padrão
        )

    # Filtrar dados pelo ano selecionado
    year_data = data[data[9].dt.year == selected_year].copy()

    # Criar uma lista de todos os meses do ano selecionado
    all_months = pd.period_range(
        start=f"{selected_year}-01",
        end=f"{selected_year}-12",
        freq="M"
    )

    # Agrupar por mês e calcular totais
    monthly_data = year_data.groupby(year_data[9].dt.to_period("M")).agg({
        5: 'count',  # Quantidade de multas
        14: 'sum'    # Valor total
    }).reset_index()

    # Ajustar o índice para incluir todos os meses
    monthly_data.set_index(9, inplace=True)
    monthly_data = monthly_data.reindex(all_months, fill_value=0).reset_index()
    monthly_data.rename(columns={
        "index": "Mês",
        5: "Quantidade_de_Multas",
        14: "Valor_Total"
    }, inplace=True)
    monthly_data["Mês"] = monthly_data["Mês"].dt.strftime('%Y-%m')

    with col2:
        # Criar figura com eixos secundários
        fig = px.line(monthly_data, x='Mês', y='Quantidade_de_Multas',
                     title=f'Multas Mensais - {selected_year}')
        
        # Adicionar linha de valor total no eixo secundário
        fig.add_scatter(x=monthly_data['Mês'], 
                       y=monthly_data['Valor_Total'],
                       name='Valor Total',
                       yaxis='y2',
                       line=dict(color='#F37529'))  # Laranja

        # Atualizar o primeiro traço (Quantidade)
        fig.data[0].update(
            name='Quantidade de Multas',
            line=dict(color='#0066B4'),  # Azul
            marker=dict(size=8, color='#0066B4')
        )
        
        # Atualizar layout
        fig.update_layout(
            template="plotly_white",
            showlegend=True,
            legend=dict(
                title=None,
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            yaxis=dict(
                title="Quantidade de Multas",
                titlefont=dict(color='#0066B4'),
                tickfont=dict(color='#0066B4')
            ),
            yaxis2=dict(
                title="Valor Total (R$)",
                titlefont=dict(color='#F37529'),
                tickfont=dict(color='#F37529'),
                overlaying='y',
                side='right',
                tickformat=',.2f',
                rangemode='tozero'
            ),
            xaxis=dict(
                tickangle=45,
                title=None,
                dtick="M1",
                tickformat="%b/%Y"
            ),
            margin=dict(t=50, b=50),
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

def create_yearly_fines_chart(data):
    """
    Cria gráfico de linhas para multas anuais com seletor de período.
    """
    # Converter coluna de data e remover valores nulos
    data = data.copy()  # Criar uma cópia para evitar SettingWithCopyWarning
    data[9] = pd.to_datetime(data[9], errors='coerce')
    
    # Filtrar apenas registros que têm multas
    data = data[data[5].notna()]
    data = data.dropna(subset=[9])

    # Remover duplicatas baseado no Auto de Infração
    data = data.drop_duplicates(subset=[5])

    # Converter valores monetários
    data[14] = (data[14].astype(str)
                .str.replace(r'[^\d,.-]', '', regex=True)
                .str.replace(',', '.')
                .astype(float))
    
    # Forçar o range de anos de 2017 até o próximo ano
    min_ano = 2017
    max_ano = datetime.now().year + 1
    anos_disponiveis = list(range(min_ano, max_ano + 1))
    
    if not anos_disponiveis:
        st.warning("Não há dados disponíveis para exibir o gráfico anual.")
        return None

    # Criar seletores de período
    col1, col2, col3 = st.columns([2, 2, 8])
    with col1:
        ano_inicio = st.selectbox(
            "Ano Inicial",
            anos_disponiveis,
            index=0
        )
    with col2:
        anos_fim = [ano for ano in anos_disponiveis if ano >= ano_inicio]
        ano_fim = st.selectbox(
            "Ano Final",
            anos_fim,
            index=len(anos_fim)-1
        )

    # Filtrar dados pelo período selecionado
    period_data = data[
        (data[9].dt.year >= ano_inicio) & 
        (data[9].dt.year <= ano_fim)
    ]

    # Criar range completo de anos
    all_years = list(range(ano_inicio, ano_fim + 1))

    # Agrupar por ano e calcular totais
    yearly_data = period_data.groupby(period_data[9].dt.year).agg({
        5: 'count',  # Quantidade de multas
        14: 'sum'    # Valor total
    }).reset_index()
    
    yearly_data.rename(columns={
        9: 'Ano',
        5: 'Quantidade_de_Multas',
        14: 'Valor_Total'
    }, inplace=True)

    # Garantir que todos os anos estejam presentes
    yearly_data = pd.DataFrame({'Ano': all_years}).merge(
        yearly_data, on='Ano', how='left'
    ).fillna(0)

    with col3:
        # Criar figura com eixos secundários
        fig = px.line(yearly_data, x='Ano', y='Quantidade_de_Multas',
                     title='Multas Acumuladas por Ano')
        
        # Adicionar linha de valor total no eixo secundário
        fig.add_scatter(x=yearly_data['Ano'], 
                       y=yearly_data['Valor_Total'],
                       name='Valor Total',
                       yaxis='y2',
                       line=dict(color='#F37529'))  # Laranja

        # Atualizar o primeiro traço (Quantidade)
        fig.data[0].update(
            name='Quantidade de Multas',
            line=dict(color='#0066B4'),  # Azul
            marker=dict(size=8, color='#0066B4')
        )
        
        # Atualizar layout
        fig.update_layout(
            template="plotly_white",
            showlegend=True,
            legend=dict(
                title=None,
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            yaxis=dict(
                title="Quantidade de Multas",
                titlefont=dict(color='#0066B4'),
                tickfont=dict(color='#0066B4'),
                rangemode='tozero'
            ),
            yaxis2=dict(
                title="Valor Total (R$)",
                titlefont=dict(color='#F37529'),
                tickfont=dict(color='#F37529'),
                overlaying='y',
                side='right',
                tickformat=',.2f',
                rangemode='tozero'
            ),
            xaxis=dict(
                tickangle=0,
                title=None,
                dtick=1,
                tickformat="d"
            ),
            margin=dict(t=50, b=50),
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)
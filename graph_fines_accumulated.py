import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
import numpy as np

def create_monthly_fines_chart(data):
    """
    Cria gráfico de linhas para multas mensais com seletor de ano.
    """
    # Converter coluna de data e remover valores nulos
    data = data.copy()  # Criar uma cópia para evitar SettingWithCopyWarning
    
    # Converter a coluna de data para datetime, tratando diferentes formatos
    def convert_date(x):
        if pd.isna(x):
            return pd.NaT
        try:
            # Tentar converter diretamente
            return pd.to_datetime(x)
        except:
            try:
                # Se for um número inteiro (ano), converter para o primeiro dia do ano
                if isinstance(x, (int, np.integer)):
                    return pd.to_datetime(f"{int(x)}-01-01")
                return pd.NaT
            except:
                return pd.NaT

    # Aplicar a conversão de data
    data[9] = data[9].apply(convert_date)
    
    # Filtrar apenas registros que têm multas e datas válidas
    data = data[data[5].notna() & data[9].notna()]
    
    # Remover duplicatas baseado no Auto de Infração
    data = data.drop_duplicates(subset=[5])

    # Converter valores monetários
    data[14] = pd.to_numeric(data[14].astype(str).str.replace(r'[^\d,.-]', '', regex=True).str.replace(',', '.'), errors='coerce')

    # Obter anos disponíveis dos dados
    anos_disponiveis = sorted(data[9].dt.year.unique())
    
    if not anos_disponiveis:
        st.warning("Não há dados disponíveis para exibir o gráfico mensal.")
        return None

    # Criar seletor de ano
    col1, col2 = st.columns([2, 8])
    with col1:
        ano_selecionado = st.selectbox(
            "Selecione o Ano",
            anos_disponiveis,
            index=len(anos_disponiveis)-1
        )

    # Filtrar dados para o ano selecionado
    dados_ano = data[data[9].dt.year == ano_selecionado]
    
    # Criar uma lista com todos os meses do ano
    todos_meses = pd.period_range(start=f"{ano_selecionado}-01", end=f"{ano_selecionado}-12", freq='M')
    
    # Agrupar por mês e calcular as métricas
    dados_mensais = (
        dados_ano.groupby(dados_ano[9].dt.to_period('M'))
        .agg({
            5: 'count',  # Quantidade de multas (contagem de Autos de Infração únicos)
            14: 'sum'   # Valor total
        })
        .reset_index()
    )
    
    # Ajustar o índice para incluir todos os meses
    dados_mensais.set_index(9, inplace=True)
    dados_mensais = dados_mensais.reindex(todos_meses, fill_value=0).reset_index()
    dados_mensais.rename(columns={
        "index": "Mês",
        5: "Quantidade_de_Multas",
        14: "Valor_Total"
    }, inplace=True)
    
    # Converter o período para datetime para o gráfico
    dados_mensais["Mês"] = dados_mensais["Mês"].dt.strftime('%Y-%m')
    
    with col2:
        # Criar figura com eixos secundários
        fig = px.line(dados_mensais, x='Mês', y='Quantidade_de_Multas',
                     title=f'Multas Mensais - {ano_selecionado}')
        
        # Adicionar linha de valor total no eixo secundário
        fig.add_scatter(x=dados_mensais['Mês'], 
                       y=dados_mensais['Valor_Total'],
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
    
    # Converter a coluna de data para datetime, tratando diferentes formatos
    def convert_date(x):
        if pd.isna(x):
            return pd.NaT
        try:
            # Tentar converter diretamente
            return pd.to_datetime(x)
        except:
            try:
                # Se for um número inteiro (ano), converter para o primeiro dia do ano
                if isinstance(x, (int, np.integer)):
                    return pd.to_datetime(f"{int(x)}-01-01")
                return pd.NaT
            except:
                return pd.NaT

    # Aplicar a conversão de data
    data[9] = data[9].apply(convert_date)
    
    # Filtrar apenas registros que têm multas e datas válidas
    data = data[data[5].notna() & data[9].notna()]
    
    # Remover duplicatas baseado no Auto de Infração
    data = data.drop_duplicates(subset=[5])

    # Converter valores monetários
    data[14] = pd.to_numeric(data[14].astype(str).str.replace(r'[^\d,.-]', '', regex=True).str.replace(',', '.'), errors='coerce')
    
    # Forçar o range de anos de 2017 até o próximo ano
    min_ano = min(data[9].dt.year.min(), 2017)
    max_ano = max(data[9].dt.year.max(), datetime.now().year + 1)
    anos_disponiveis = list(range(min_ano, max_ano + 1))
    
    if not anos_disponiveis:
        st.warning("Não há dados disponíveis para exibir o gráfico anual.")
        return None

    # Criar seletores de período
    col1, col2, col3 = st.columns([2, 2, 8])
    with col1:
        ano_inicio = st.selectbox(
            "Ano Inicial",
            anos_disponiveis[:-1],  # Excluir o último ano da lista
            index=0
        )
    
    with col2:
        # Filtrar anos finais possíveis (sempre maior que ano inicial)
        anos_finais = [ano for ano in anos_disponiveis if ano > ano_inicio]
        if not anos_finais:
            anos_finais = [ano_inicio + 1]
        
        ano_fim = st.selectbox(
            "Ano Final",
            anos_finais,
            index=len(anos_finais)-1
        )

    # Filtrar dados pelo período selecionado
    mask_periodo = (data[9].dt.year >= ano_inicio) & (data[9].dt.year <= ano_fim)
    dados_periodo = data[mask_periodo]

    # Agrupar por ano e calcular métricas
    dados_anuais = (
        dados_periodo.groupby(dados_periodo[9].dt.year)
        .agg({
            5: 'count',  # Quantidade de multas
            14: 'sum'    # Valor total
        })
        .reset_index()
    )

    # Renomear colunas
    dados_anuais.columns = ['Ano', 'Quantidade_de_Multas', 'Valor_Total']

    with col3:
        # Criar o gráfico
        fig = px.line(
            dados_anuais,
            x='Ano',
            y=['Quantidade_de_Multas', 'Valor_Total'],
            title='Multas Acumuladas por Ano',
            labels={
                'value': 'Valores',
                'variable': 'Métricas',
                'Ano': 'Ano'
            },
            markers=True
        )

        # Ajustar layout
        fig.update_traces(marker=dict(size=8))
        fig.update_layout(
            xaxis_title='',
            yaxis_title='Valores',
            template='plotly_white',
            legend_title='Métricas',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)
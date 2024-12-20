import pandas as pd
import plotly.express as px
from datetime import datetime

def create_fines_accumulated_chart(data, period='M'):
    """
    Cria um gráfico de linhas para exibir a quantidade e o valor acumulado de multas por período (2024).

    Parâmetros:
        data (DataFrame): Os dados filtrados contendo informações sobre as multas.
        period (str): O período para agrupamento ('M' para mensal, 'W' para semanal).

    Retorna:
        fig (plotly.graph_objects.Figure): Um gráfico de linhas mostrando quantidade e valor acumulado de multas.
    """
    # Garantir que a coluna com índice 9 (Data da Infração) seja datetime
    data[9] = pd.to_datetime(data[9], errors='coerce')

    # Remover linhas com datas inválidas
    data = data.dropna(subset=[9])
    
    # Filtrar apenas o ano atual (de janeiro a dezembro)
    current_year = datetime.now().year
    data = data[(data[9] >= pd.Timestamp(f"{current_year}-01-01")) & (data[9] <= pd.Timestamp(f"{current_year}-12-31"))]

    # Garantir que a coluna com índice 14 (Valor a ser pago R$) esteja em formato numérico
    data[14] = (
        data[14]
        .astype(str)
        .str.replace(r'[^\d,.-]', '', regex=True)
        .str.replace(',', '.')
        .astype(float)
    )

    # Criar um campo de período com base nos meses do ano
    data['Período'] = data[9].dt.to_period('M').dt.to_timestamp()

    # Agregar dados: contar multas e somar valores por período
    fines_by_period = data.groupby('Período').agg(
        Quantidade_de_Multas=(5, 'nunique'),  # Índice 5 representa 'Auto de Infração'
        Valor_Total=(14, 'sum')               # Índice 14 representa 'Valor a ser pago R$'
    ).reset_index()

    # Criar o gráfico com duas linhas: Quantidade de Multas e Valor Total
    fig = px.line(
        fines_by_period,
        x='Período',
        y=['Quantidade_de_Multas', 'Valor_Total'],
        labels={
            'value': 'Total de Multas',
            'Período': 'Período'
        },
        title=''
    )

    # Personalizar o layout
    fig.update_traces(mode='lines+markers', marker=dict(size=8))
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Valores",
        template="plotly_white",
        legend=dict(title="Métricas")
    )

    return fig

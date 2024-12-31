import pandas as pd
import plotly.express as px
from datetime import datetime

def create_monthly_fines_chart(data):
    """
    Cria gráfico de linhas para multas mensais do ano atual.
    """
    data[9] = pd.to_datetime(data[9], errors='coerce')
    data = data.dropna(subset=[9])
    
    current_year = datetime.now().year
    data = data[(data[9].dt.year == current_year)]

    data[14] = (data[14].astype(str)
                .str.replace(r'[^\d,.-]', '', regex=True)
                .str.replace(',', '.')
                .astype(float))

    monthly_data = data.groupby(data[9].dt.strftime('%Y-%m')).agg(
        Quantidade_de_Multas=(5, 'nunique'),
        Valor_Total=(14, 'sum')
    ).reset_index()
    monthly_data.rename(columns={9: 'Mês'}, inplace=True)

    fig = px.line(monthly_data,
                 x='Mês',
                 y=['Quantidade_de_Multas', 'Valor_Total'],
                 labels={'value': 'Total', 'Mês': ''},
                 title='Multas Mensais - ' + str(current_year))

    fig.update_traces(mode='lines+markers', marker=dict(size=8))
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Valores",
        template="plotly_white",
        legend=dict(title="Métricas"),
        yaxis=dict(range=[0, monthly_data['Valor_Total'].max() * 1.1])
    )

    fig.update_layout(
        yaxis=dict(
            range=[0, monthly_data['Valor_Total'].max() * 1.2],
            title="Valores"
        ),
        yaxis2=dict(
            range=[0, monthly_data['Quantidade_de_Multas'].max() * 1.2],
            title="Quantidade",
            overlaying='y',
            side='right'
        )
    )

    return fig

def create_yearly_fines_chart(data):
    """
    Cria gráfico de linhas para multas anuais.
    """
    data[9] = pd.to_datetime(data[9], errors='coerce')
    data = data.dropna(subset=[9])

    data[14] = (data[14].astype(str)
                .str.replace(r'[^\d,.-]', '', regex=True)
                .str.replace(',', '.')
                .astype(float))

    yearly_data = data.groupby(data[9].dt.year).agg(
        Quantidade_de_Multas=(5, 'nunique'),
        Valor_Total=(14, 'sum')
    ).reset_index()
    yearly_data.rename(columns={9: 'Ano'}, inplace=True)

    fig = px.line(yearly_data,
                 x='Ano',
                 y=['Quantidade_de_Multas', 'Valor_Total'],
                 labels={'value': 'Total', 'Ano': ''},
                 title='Multas Acumuladas por Ano')

    fig.update_traces(mode='lines+markers', marker=dict(size=8))
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Valores",
        template="plotly_white",
        legend=dict(title="Métricas"),
        yaxis=dict(range=[0, yearly_data['Valor_Total'].max() * 1.1])
    )

    return fig
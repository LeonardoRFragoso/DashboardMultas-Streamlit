import pandas as pd
import plotly.express as px
from datetime import datetime

def get_vehicle_fines_data(df):
    """
    Processa os dados para obter veículos com mais multas e seus valores totais.

    Parâmetros:
        df (DataFrame): O conjunto de dados contendo informações sobre multas.

    Retorna:
        DataFrame: Um DataFrame com os dados agregados por veículo.
    """
    # Índices corretos das colunas
    plate_column = 1  # Índice da coluna 'Placa Relacionada'
    value_column = 14  # Índice da coluna 'Valor a ser pago R$'
    infraction_column = 5  # Índice da coluna 'Auto de Infração'
    date_column = 9  # Índice da coluna 'Data da Infração'

    # Verificar colunas essenciais
    required_columns = [plate_column, value_column, infraction_column, date_column]
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"A coluna com índice {col} não está presente no DataFrame.")

    # Copiar o DataFrame
    df = df.copy()

    # Converter 'Data da Infração' para datetime e filtrar apenas o ano atual
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce', dayfirst=True)
    df = df[df[date_column].dt.year == datetime.now().year]

    # Garantir que 'Valor a ser pago R$' esteja no formato numérico
    try:
        df[value_column] = (
            df[value_column]
            .astype(str)
            .str.replace(r'[^\d,.-]', '', regex=True)  # Remove caracteres não numéricos
            .str.replace(',', '.')
            .astype(float)
            .fillna(0)
        )
    except ValueError as e:
        raise ValueError(f"Erro ao converter valores monetários: {e}")

    # Remover duplicatas baseadas no 'Auto de Infração' (registro único de multa)
    df = df.drop_duplicates(subset=[infraction_column])

    # Remover registros com placas nulas ou inválidas
    df = df.dropna(subset=[plate_column])

    # Agrupar os dados por 'Placa Relacionada'
    fines_by_vehicle = df.groupby(plate_column).agg(
        total_fines=(value_column, 'sum'),
        num_fines=(infraction_column, 'nunique')  # Contar apenas multas únicas
    ).reset_index()

    # Renomear as colunas para facilitar a leitura no gráfico
    fines_by_vehicle.rename(columns={
        plate_column: 'Placa Relacionada'
    }, inplace=True)

    # Ordenar por número de multas em ordem decrescente
    fines_by_vehicle = fines_by_vehicle.sort_values(by='num_fines', ascending=False)

    return fines_by_vehicle

def create_vehicle_fines_chart(df):
    """
    Cria um gráfico de barras para os veículos com mais multas.

    Parâmetros:
        df (DataFrame): O conjunto de dados contendo informações sobre multas.

    Retorna:
        plotly.graph_objects.Figure: Um gráfico de barras mostrando os 10 veículos principais.
    """
    # Processar os dados
    fines_by_vehicle = get_vehicle_fines_data(df)

    # Verificar se há dados suficientes
    if fines_by_vehicle.empty:
        raise ValueError("Nenhum dado disponível para gerar o gráfico. Verifique os dados filtrados.")

    # Criar o gráfico
    fig = px.bar(
        fines_by_vehicle.head(10),  # Top 10 veículos
        x='Placa Relacionada',
        y='total_fines',
        color='num_fines',
        text='num_fines',
        labels={
            'Placa Relacionada': 'Veículo (Placa Relacionada)',
            'total_fines': 'Total das Multas (R$)',
            'num_fines': 'Número de Multas'
        }
    )

    # Ajustar o estilo do gráfico
    fig.update_traces(
        texttemplate='%{text} multas<br>R$ %{y:,.2f}',
        textposition='inside'
    )

    fig.update_layout(
        title="",
        xaxis_title='',
        yaxis_title='Total das Multas (R$)',
        coloraxis_colorbar=dict(title='Número de Multas'),
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

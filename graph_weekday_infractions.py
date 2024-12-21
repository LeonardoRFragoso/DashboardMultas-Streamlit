import pandas as pd
import plotly.express as px

def create_weekday_infractions_chart(data):
    """
    Create a bar chart to display the number of fines distributed by day of the week.

    Parameters:
        data (DataFrame): The filtered data containing fines information.

    Returns:
        fig (plotly.graph_objects.Figure): A bar chart showing the distribution of fines by day of the week.
    """
    # Verificar se a coluna 'Data da Infração' (índice 9) existe
    if 9 not in data.columns:
        raise KeyError("A coluna com índice 9 (Data da Infração) não está presente no DataFrame.")

    # Garantir que a coluna com índice 9 é um objeto datetime
    data[9] = pd.to_datetime(data[9], errors='coerce')

    # Remover datas inválidas
    data = data.dropna(subset=[9])

    # Mapear os dias da semana
    dias_semana = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira',
        3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'
    }
    data['Dia da Semana'] = data[9].dt.weekday.map(dias_semana)

    # Contar a quantidade de multas por dia da semana
    weekday_counts = data['Dia da Semana'].value_counts().reindex(
        ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
    ).reset_index()
    weekday_counts.columns = ['Dia da Semana', 'Quantidade de Multas']

    # Criar o gráfico de barras sem título
    fig = px.bar(
        weekday_counts,
        x='Dia da Semana',
        y='Quantidade de Multas',
        text='Quantidade de Multas',  # Adiciona texto com a quantidade de multas
        labels={
            'Dia da Semana': 'Dia da Semana',
            'Quantidade de Multas': 'Quantidade de Multas'
        }
    )

    # Atualizar layout para exibir texto dentro das barras
    fig.update_traces(
        texttemplate='%{text}',  # Mostra apenas a quantidade de multas
        textposition='inside'  # Posição do texto dentro das barras
    )

    fig.update_layout(
        title="",  # Remove o título automático
        xaxis_title="",
        yaxis_title="Quantidade de Multas",
        template="plotly_white",  # Tema claro
        uniformtext_minsize=16,
        uniformtext_mode='hide'  # Evita sobreposição de textos
    )

    return fig

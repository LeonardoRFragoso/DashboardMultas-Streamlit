import pandas as pd
import plotly.express as px

def create_common_infractions_chart(data):
   """
   Create a bar chart to display the most common infractions and their descriptions.

   Parameters:
       data (DataFrame): The filtered data containing fines information.

   Returns:
       fig (plotly.graph_objects.Figure): A bar chart of the most common infractions.
   """
   infraction_column = 8  # Índice da coluna 'Enquadramento da Infração'
   description_column = 11  # Índice da coluna 'Descrição'
   auto_infraction_column = 5  # Índice da coluna 'Auto de Infração'

   # Verificar se os índices estão presentes no DataFrame
   required_columns = [infraction_column, description_column, auto_infraction_column]
   for col in required_columns:
       if col not in data.columns:
           raise KeyError(f"A coluna com índice {col} não está presente no DataFrame.")

   # Agrupar primeiro por descrição para combinar ocorrências do mesmo tipo
   infraction_data = (data.groupby([description_column, infraction_column])[auto_infraction_column]
                     .count()
                     .reset_index()
                     .groupby(description_column)
                     .agg({
                         infraction_column: 'first',
                         auto_infraction_column: 'sum'
                     })
                     .reset_index())

   # Renomear colunas para facilitar a manipulação
   infraction_data.columns = ['Descrição', 'Enquadramento', 'Frequência']

   # Ordenar pelos mais frequentes
   infraction_data = infraction_data.sort_values(by='Frequência', ascending=False).head(10)

   # Criar o texto formatado lado a lado
   infraction_data['Texto'] = (
       infraction_data['Enquadramento'] + " | " +
       infraction_data['Frequência'].astype(str) + " ocorrências"
   )

   # Criar o gráfico de barras
   fig = px.bar(
       infraction_data,
       x='Frequência',
       y='Descrição',
       text='Texto',
       orientation='h',
       labels={'Descrição': ''}  # Remove o título automático do eixo Y
   )

   # Ajustar a legibilidade do texto
   fig.update_traces(
       texttemplate='%{text}',
       textposition='inside',
       insidetextanchor='middle',
       textfont=dict(size=16, color='white'),
       marker_color='#007bff'
   )

   # Ajustar layout para remover o subtítulo duplicado
   fig.update_layout(
       title="",  # Remover o título automático
       xaxis=dict(visible=False),  # Remove eixo X
       yaxis=dict(title=None, showticklabels=True),  # Remove título do eixo Y
       title_x=0.5,  # Centraliza o título (caso seja reinserido manualmente)
       margin=dict(l=50, r=50, t=50, b=50),
       template="plotly_white",
       showlegend=False  # Remove qualquer legenda
   )

   return fig
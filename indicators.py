import streamlit as st
import pandas as pd
from datetime import datetime

def render_css():
   st.markdown(
       """
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
               cursor: pointer;
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
       </style>
       """,
       unsafe_allow_html=True,
   )

def render_indicators(data, filtered_data, data_inicio, data_fim):
   render_css()

   if 5 in data.columns:
       unique_fines = data.drop_duplicates(subset=[5])
   else:
       st.error("A coluna com índice 5 não foi encontrada nos dados.")
       unique_fines = pd.DataFrame(columns=[5, 14, 9])

   total_multas = unique_fines[5].nunique() if 5 in unique_fines.columns else 0
   valor_total_multas = unique_fines[14].sum() if 14 in unique_fines.columns else 0
   ano_atual = datetime.now().year
   mes_atual = data_fim.month if data_fim else datetime.now().month

   multas_ano_atual = unique_fines[unique_fines[9].dt.year == ano_atual][5].nunique() if 9 in unique_fines.columns else 0
   valor_multas_ano_atual = unique_fines[unique_fines[9].dt.year == ano_atual][14].sum() if 14 in unique_fines.columns else 0

   multas_mes_atual = filtered_data[
       (filtered_data[9].dt.year == ano_atual) & (filtered_data[9].dt.month == mes_atual)
   ][5].nunique() if 9 in filtered_data.columns else 0

   valor_multas_mes_atual = filtered_data[
       (filtered_data[9].dt.year == ano_atual) & (filtered_data[9].dt.month == mes_atual)
   ][14].sum() if 14 in filtered_data.columns else 0

   try:
       data_consulta = data.iloc[1, 0]
       data_formatada = (
           data_consulta.strftime('%d/%m/%Y %H:%M')
           if isinstance(data_consulta, pd.Timestamp) else str(data_consulta)
       )
   except (IndexError, KeyError):
       data_formatada = "N/A"

   indicadores_html = f"""
   <div class="indicadores-container">
       <div class="indicador" data-id="total_multas">
           <span>Total de Multas</span>
           <p>{total_multas}</p>
       </div>
       <div class="indicador" data-id="valor_total">
           <span>Valor Total das Multas</span>
           <p>R$ {valor_total_multas:,.2f}</p>
       </div>
       <div class="indicador" data-id="multas_ano">
           <span>Multas no Ano Atual</span>
           <p>{multas_ano_atual}</p>
       </div>
       <div class="indicador" data-id="valor_ano">
           <span>Valor Total Multas no Ano Atual</span>
           <p>R$ {valor_multas_ano_atual:,.2f}</p>
       </div>
       <div class="indicador" data-id="multas_mes">
           <span>Multas no Mês Atual</span>
           <p>{multas_mes_atual}</p>
       </div>
       <div class="indicador" data-id="valor_mes">
           <span>Valor das Multas no Mês Atual</span>
           <p>R$ {valor_multas_mes_atual:,.2f}</p>
       </div>
       <div class="indicador" data-id="data_consulta">
           <span>Última Atualização</span>
           <p>{data_formatada}</p>
       </div>
   </div>
   
   <script>
       const indicadores = document.querySelectorAll('.indicador');
       indicadores.forEach(indicador => {{
           indicador.addEventListener('dblclick', function() {{
               const indicatorId = this.getAttribute('data-id');
               fetch(`/abrir_planilha?id=${{indicatorId}}`);
           }});
       }});
   </script>
   """

   st.markdown(indicadores_html, unsafe_allow_html=True)
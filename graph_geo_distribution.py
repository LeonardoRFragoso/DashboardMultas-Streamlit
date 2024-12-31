import folium
import pandas as pd
from geo_utils import load_cache, save_cache, get_cached_coordinates
from streamlit_folium import st_folium

def create_geo_distribution_map(filtered_data, api_key):
   """
   Create a geographical map for fines distribution.
   
   Parameters:
       filtered_data (DataFrame): The filtered data containing fines information.
       api_key (str): The API key for geocoding services.

   Returns:
       map_object (folium.Map): The generated folium map.
   """
   coordinates_cache = load_cache()
   
   # Indices das colunas
   local_infracao = 12  # Local da Infração
   valor_pagar = 14     # Valor a ser pago R$
   data_infracao = 9    # Data da Infração
   
   required_columns = [local_infracao, valor_pagar, data_infracao]
   for col in required_columns:
       if col not in filtered_data.columns:
           raise KeyError(f"A coluna com índice {col} não está presente no DataFrame.")

   map_data = filtered_data.dropna(subset=[local_infracao]).copy()
   map_data[['Latitude', 'Longitude']] = map_data[local_infracao].apply(
       lambda x: pd.Series(get_cached_coordinates(x, api_key))
   )

   if not map_data.empty:
       map_center = [map_data['Latitude'].mean(), map_data['Longitude'].mean()]
   else:
       map_center = [-22.9068, -43.1729]  # Coordenadas padrão - Rio de Janeiro

   # Criar mapa com tema escuro
   map_object = folium.Map(
       location=map_center, 
       zoom_start=8, 
       tiles="CartoDB dark_matter"
   )

   # Ícone personalizado
   icon_url = "https://cdn-icons-png.flaticon.com/512/1828/1828843.png"
   icon_size = (30, 30)

   for _, row in map_data.iterrows():
       if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
           popup_content = f"""
           <b>Local:</b> {row[local_infracao]}<br>
           <b>Valor:</b> R$ {row[valor_pagar]:,.2f}<br>
           <b>Data da Infração:</b> {row[data_infracao].strftime('%d/%m/%Y') if pd.notnull(row[data_infracao]) else "Não disponível"}
           """
           marker = folium.Marker(
               location=[row['Latitude'], row['Longitude']],
               popup=folium.Popup(popup_content, max_width=300),
               icon=folium.CustomIcon(icon_url, icon_size=icon_size)
           )
           marker.add_to(map_object)

   return map_object
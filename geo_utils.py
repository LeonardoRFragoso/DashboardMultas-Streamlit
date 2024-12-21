import os
import json
import requests
import streamlit as st

# Caminho do arquivo de cache de coordenadas
CACHE_FILE = "coordinates_cache.json"

def initialize_cache():
    """
    Inicializa o cache de coordenadas no st.session_state.
    Carrega do arquivo ou cria um novo cache vazio.
    """
    if 'cache' not in st.session_state:
        st.session_state.cache = load_cache()

def load_cache():
    """
    Carrega o cache do arquivo JSON.

    Returns:
        dict: O cache carregado, ou um dicionário vazio caso não exista.
    """
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as file:
                return json.load(file)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar o cache: {e}")
    return {}

def save_cache():
    """
    Salva o cache do st.session_state no arquivo JSON.
    """
    try:
        with open(CACHE_FILE, 'w') as file:
            json.dump(st.session_state.cache, file, indent=4)
    except IOError as e:
        print(f"Erro ao salvar o cache: {e}")

def get_coordinates(local, api_key):
    """
    Busca as coordenadas para um local usando a API OpenCage.

    Parameters:
        local (str): O local para buscar as coordenadas.
        api_key (str): A chave de API do OpenCage.

    Returns:
        tuple: Uma tupla (latitude, longitude) ou (None, None) caso falhe.
    """
    url = f"https://api.opencagedata.com/geocode/v1/json?q={local}&key={api_key}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'results' in data and data['results']:
            geometry = data['results'][0]['geometry']
            lat, lng = geometry['lat'], geometry['lng']
            if lat is not None and lng is not None:
                return lat, lng
        print(f"Nenhum resultado válido encontrado para o local: {local}")
    except requests.RequestException as e:
        print(f"Erro ao buscar coordenadas: {e}")
    return None, None

def get_cached_coordinates(local, api_key):
    """
    Obtém coordenadas do cache ou faz a busca na API e atualiza o cache.

    Parameters:
        local (str): O local a ser buscado.
        api_key (str): A chave de API.

    Returns:
        tuple: Uma tupla (latitude, longitude).
    """
    # Inicializar cache se ainda não estiver carregado
    initialize_cache()

    cache = st.session_state.cache

    # Busca no cache
    if local in cache:
        lat, lng = cache[local]
        if lat is not None and lng is not None:
            return lat, lng

    # Caso não esteja no cache, buscar na API
    lat, lng = get_coordinates(local, api_key)
    if lat is not None and lng is not None:
        cache[local] = (lat, lng)
        save_cache()  # Atualiza o cache no disco
        return lat, lng

    # Retorno padrão em caso de falha
    return None, None

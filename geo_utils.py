import os
import json
import requests
import streamlit as st
import time
import unicodedata
from geo_utils import load_cache

CACHE_FILE = "coordinates_cache.json"
LAST_SAVE_TIME = time.time()

def initialize_cache():
    if 'cache' not in st.session_state:
        st.session_state.cache = load_cache()

initialize_cache()  # Inicializar no carregamento do módulo

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as file:
                return json.load(file)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar o cache: {e}")
    return {}

def save_cache():
    try:
        with open(CACHE_FILE, 'w') as file:
            json.dump(st.session_state.cache, file, indent=4)
    except IOError as e:
        print(f"Erro ao salvar o cache: {e}")

def save_cache_throttled(interval=30):
    global LAST_SAVE_TIME
    if time.time() - LAST_SAVE_TIME > interval:
        save_cache()
        LAST_SAVE_TIME = time.time()

def normalize_text(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower().strip()

def get_coordinates(local, api_key, timeout=15):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={local}&key={api_key}"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        if 'results' in data and data['results']:
            geometry = data['results'][0]['geometry']
            lat, lng = geometry['lat'], geometry['lng']
            if lat and lng:
                return lat, lng
        print(f"Nenhum resultado válido para o local: {local}")
    except requests.RequestException as e:
        print(f"Erro ao buscar coordenadas: {e}")
    return None, None

def get_cached_coordinates(local, api_key):
    initialize_cache()
    cache = st.session_state.cache
    normalized_local = normalize_text(local)

    if normalized_local in cache:
        lat, lng = cache[normalized_local]
        if lat is not None and lng is not None:
            return lat, lng

    lat, lng = get_coordinates(normalized_local, api_key)
    if lat is not None and lng is not None:
        cache[normalized_local] = (lat, lng)
        save_cache_throttled()  # Salvar apenas periodicamente

    return lat, lng

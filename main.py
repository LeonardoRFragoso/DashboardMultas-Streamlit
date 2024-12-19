from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import streamlit as st
from dashboard import render_dashboard
import json

def main():
    # Configurações iniciais
    st.set_page_config(page_title="Torre de Controle - Dashboard de Multas", layout="wide")

    # Configurações de credenciais
    try:
        credentials_json = st.secrets["general"]["CREDENTIALS"]
        if isinstance(credentials_json, str):
            credentials_json = json.loads(credentials_json)  # Certifica que é convertido para dict

        credentials = Credentials.from_service_account_info(
            credentials_json, scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive_service = build("drive", "v3", credentials=credentials)
    except Exception as e:
        st.error(f"Erro ao configurar o serviço do Google Drive: {e}")
        return

    # Obter ID da planilha
    try:
        ultima_planilha_id = st.secrets["drive"]["ultima_planilha_id"]
    except KeyError as e:
        st.error(f"Erro ao acessar o ID da planilha: {e}")
        return

    # Renderizar o Dashboard
    try:
        render_dashboard(file_id=ultima_planilha_id, drive_service=drive_service)
    except Exception as e:
        st.error(f"Erro ao renderizar o dashboard: {e}")

if __name__ == "__main__":
    main()

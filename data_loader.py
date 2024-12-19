import pandas as pd
import tempfile
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import json

def get_drive_service(credentials_json):
    try:
        if isinstance(credentials_json, str):
            credentials_json = json.loads(credentials_json)

        if not isinstance(credentials_json, dict):
            raise ValueError("As credenciais fornecidas não são válidas.")

        credentials = Credentials.from_service_account_info(
            credentials_json, scopes=["https://www.googleapis.com/auth/drive"]
        )
        return build('drive', 'v3', credentials=credentials)
    except Exception as e:
        raise ValueError(f"Erro ao configurar o serviço do Google Drive: {e}")

def carregar_planilha(file_id, drive_service):
    try:
        # Baixar a planilha do Google Drive
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            request = drive_service.files().get_media(fileId=file_id)
            tmp_file.write(request.execute())
            tmp_file_path = tmp_file.name
        df = pd.read_excel(tmp_file_path, header=0)

        # Verificar estrutura básica de colunas por índice
        required_indices = [0, 5, 9, 14, 15]  # Índices das colunas esperadas
        for idx in required_indices:
            if idx >= len(df.columns):
                raise KeyError(f"A coluna de índice {idx} não foi encontrada no arquivo carregado.")

        return df

    except Exception as e:
        raise ValueError(f"Erro ao carregar a planilha do Google Drive: {e}")

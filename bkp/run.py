import streamlit as st
import pandas as pd
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import tempfile

# Configuração do Streamlit e Google Drive
st.set_page_config(page_title="Torre de Controle - Dashboard de Multas", layout="wide")

secrets = st.secrets
credentials_json = json.loads(secrets["general"]["CREDENTIALS"])
ultima_planilha_id = secrets["drive"]["ultima_planilha_id"]
logo_url = secrets["image"]["logo_url"]

credentials = Credentials.from_service_account_info(
    credentials_json, scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build('drive', 'v3', credentials=credentials)

@st.cache_data
def carregar_planilha(file_id):
    try:
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            request = drive_service.files().get_media(fileId=file_id)
            tmp_file.write(request.execute())
            tmp_file_path = tmp_file.name
        return pd.read_excel(tmp_file_path, header=0)
    except Exception as e:
        st.error(f"Erro ao carregar a planilha: {e}")
        raise

# Estilo customizado para o dashboard
st.markdown(
    """
    <style>
    .main-container {
        padding: 0;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    .title-container {
        background: linear-gradient(90deg, #F37529, #FFDDC1);
        color: white;
        text-align: center;
        padding: 15px 0;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .indicadores-container {
        display: flex;
        justify-content: space-around;
        text-align: center;
        margin-bottom: 40px;
    }
    .indicador {
        background: #FFFFFF;
        padding: 20px 40px;
        border-radius: 12px;
        border: 2px solid #F37529;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .indicador:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    .footer {
        margin-top: 50px;
        text-align: center;
        font-size: 14px;
        color: #888;
        padding: 10px;
        background-color: #f9f9f9;
        border-top: 1px solid #eee;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Exibir logo
st.markdown(
    f"""
    <div class="logo-container">
        <img src="{logo_url}" alt="Logo" width="150">
    </div>
    """,
    unsafe_allow_html=True,
)

# Título do dashboard
st.markdown(
    """
    <div class="title-container">
        <h1>Torre de Controle - Dashboard de Multas</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# Carregar dados
try:
    df = carregar_planilha(ultima_planilha_id)
    st.success("Dados carregados com sucesso!")
except Exception as e:
    st.error("Erro ao carregar os dados. Verifique as credenciais e o ID do arquivo.")
    st.stop()

# Selecionar colunas pela referência
try:
    df["Dia da Consulta"] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')  # Coluna A
    df["Auto de Infração"] = df.iloc[:, 5].astype(str).str.strip()  # Coluna F
    df["Data da Infração"] = pd.to_datetime(df.iloc[:, 9], dayfirst=True, errors='coerce')  # Coluna J
    df["Valor Calculado"] = pd.to_numeric(
        df.iloc[:, 14].replace({r'[^0-9,\. ]': '', ',': '.'}, regex=True), errors='coerce'
    ).fillna(0)  # Coluna O
    df["Status de Pagamento"] = df.iloc[:, 15].astype(str).str.strip()  # Coluna P
except Exception as e:
    st.error("Erro ao processar as colunas. Verifique os dados da planilha.")
    st.stop()

# Filtrar dados para o último dia e remover duplicados
ultimo_dia = df["Dia da Consulta"].max()
if pd.isnull(ultimo_dia):
    st.error("Não foi possível identificar o último dia nos dados carregados.")
    st.stop()

df_ultimo_dia = df[df["Dia da Consulta"] == ultimo_dia]
df_ultimo_dia = df_ultimo_dia.drop_duplicates(subset=["Auto de Infração", "Data da Infração", "Valor Calculado"])

# Aplicar validação de padrão para "Auto de Infração"
padrao_auto_infracao = r'^[A-Z]{1}\d{8}$'  # Exemplo: "I46521024"
df_ultimo_dia = df_ultimo_dia[df_ultimo_dia["Auto de Infração"].str.match(padrao_auto_infracao, na=False)]

# Total de registros únicos
num_registros_unicos = len(df_ultimo_dia)

# Valor total a ser pago
valor_total_ultimo_dia = df_ultimo_dia["Valor Calculado"].sum()

# Indicadores principais
st.markdown(
    f"""
    <div class="indicadores-container">
        <div class="indicador">
            <h3>Total de Registros Únicos</h3>
            <p>{num_registros_unicos}</p>
        </div>
        <div class="indicador">
            <h3>Valor Total a Pagar</h3>
            <p>R$ {valor_total_ultimo_dia:,.2f}</p>
        </div>
        <div class="indicador">
            <h3>Última Consulta</h3>
            <p>{ultimo_dia.strftime('%d/%m/%Y')}</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Footer
st.markdown(
    """
    <div class="footer">
        Dashboard de Multas © 2024 | Desenvolvido pela Equipe de Qualidade
    </div>
    """,
    unsafe_allow_html=True,
)

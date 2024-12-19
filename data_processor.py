import pandas as pd

def processar_dados(df):
    """
    Processa os dados carregados, aplicando filtros e cálculos necessários para o dashboard.
    """
    try:
        # Conversões de colunas
        df["Dia da Consulta"] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors="coerce")  # Coluna A
        df["Auto de Infração"] = df.iloc[:, 5].astype(str).str.strip()  # Coluna F
        df["Data da Infração"] = pd.to_datetime(df.iloc[:, 9], dayfirst=True, errors="coerce")  # Coluna J

        # Converte valores monetários para numéricos
        df["Valor Calculado"] = pd.to_numeric(
            df.iloc[:, 14].replace({r"[^0-9,.-]": "", ",": "."}, regex=True), errors="coerce"
        ).fillna(0)

        df["Status de Pagamento"] = df.iloc[:, 15].astype(str).str.strip()  # Coluna P

        # Filtrar pelo último dia da consulta
        ultimo_dia = df["Dia da Consulta"].max()
        df_ultimo_dia = df[df["Dia da Consulta"] == ultimo_dia].drop_duplicates(
            subset=["Auto de Infração", "Data da Infração", "Valor Calculado"]
        )

        # Validar padrão "Auto de Infração"
        padrao_auto_infracao = r"^[A-Z]{1}\d{8}$"
        df_ultimo_dia = df_ultimo_dia[df_ultimo_dia["Auto de Infração"].str.match(padrao_auto_infracao, na=False)]

        return df_ultimo_dia, ultimo_dia

    except Exception as e:
        raise Exception(f"Erro ao processar os dados: {e}")

import pandas as pd

def clean_data(df):
    """
    Limpa e padroniza os dados de um DataFrame, ajustando colunas específicas
    e garantindo que estejam no formato correto.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados originais.

    Returns:
        pd.DataFrame: DataFrame limpo e padronizado.
    """
    # Ajustar nomes de colunas
    df.columns = df.columns.str.strip()

    # Verificar se as colunas necessárias estão presentes
    required_columns = ["Valor a ser pago R$", "Dia da Consulta", "Auto de Infração"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"A coluna '{col}' não foi encontrada nos dados.")

    # Limpar e converter a coluna 'Valor a ser pago R$' para numérico
    df["Valor a ser pago R$"] = pd.to_numeric(
        df["Valor a ser pago R$"].replace({r"[^0-9,\.]": "", ",": "."}, regex=True),
        errors="coerce"
    ).fillna(0)

    # Converter a coluna 'Dia da Consulta' para formato datetime
    df["Dia da Consulta"] = pd.to_datetime(df["Dia da Consulta"], dayfirst=True, errors="coerce")

    # Adicionar validação e conversão para colunas adicionais, se aplicável
    if "Data da Infração" in df.columns:
        df["Data da Infração"] = pd.to_datetime(df["Data da Infração"], dayfirst=True, errors="coerce")

    # Validar o padrão da coluna 'Auto de Infração'
    padrao_auto_infracao = r"^[A-Z]{1}\d{8}$"
    df["Auto de Infração"] = df["Auto de Infração"].astype(str).str.strip()
    df = df[df["Auto de Infração"].str.match(padrao_auto_infracao, na=False)]

    return df

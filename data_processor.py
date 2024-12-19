import pandas as pd

def processar_dados(df):
    """
    Processa os dados carregados, aplicando filtros e cálculos necessários para o dashboard.
    """
    try:
        # Conversões de colunas por índice
        df["Dia da Consulta"] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors="coerce")  # Coluna A
        df["Auto de Infração"] = df.iloc[:, 5].astype(str).str.strip()  # Coluna F
        df["Data da Infração"] = pd.to_datetime(df.iloc[:, 9], dayfirst=True, errors="coerce")  # Coluna J

        # Substituir valores inválidos em 'Valor Calculado' (Coluna O - índice 14)
        df["Valor Calculado"] = (
            df.iloc[:, 14]
            .astype(str)
            .str.replace(r"[^0-9,.-]", "", regex=True)  # Remove caracteres inválidos
            .str.replace(",", ".")  # Substitui vírgula por ponto para valores decimais
            .replace("", "0")  # Substituir strings vazias por "0"
        )

        # Logar valores inválidos para depuração
        invalid_values = df[~df["Valor Calculado"].str.match(r"^-?\d+(\.\d+)?$", na=False)]
        if not invalid_values.empty:
            print(f"Valores inválidos encontrados: {invalid_values['Valor Calculado'].tolist()}")

        # Converter para numérico
        df["Valor Calculado"] = pd.to_numeric(df["Valor Calculado"], errors="coerce").fillna(0)

        # Verificar se 'ultimo_dia' é válido
        ultimo_dia = df["Dia da Consulta"].max()
        if pd.isna(ultimo_dia):
            raise ValueError("Não há datas válidas na coluna 'Dia da Consulta'.")

        # Filtrar pelo último dia da consulta
        df_ultimo_dia = df[df["Dia da Consulta"] == ultimo_dia].drop_duplicates(
            subset=["Auto de Infração", "Data da Infração", "Valor Calculado"]
        )

        # Validar padrão "Auto de Infração"
        padrao_auto_infracao = r"^[A-Z]{1}\d{8}$"
        registros_invalidos = df_ultimo_dia[~df_ultimo_dia["Auto de Infração"].str.match(padrao_auto_infracao, na=False)]
        if not registros_invalidos.empty:
            print(f"Registros inválidos em 'Auto de Infração': {registros_invalidos['Auto de Infração'].tolist()}")

        df_ultimo_dia = df_ultimo_dia[df_ultimo_dia["Auto de Infração"].str.match(padrao_auto_infracao, na=False)]

        return df_ultimo_dia, ultimo_dia

    except KeyError as ke:
        raise KeyError(f"Erro nas colunas do DataFrame: {ke}")
    except ValueError as ve:
        raise ValueError(f"Erro nos valores do DataFrame: {ve}")
    except Exception as e:
        raise Exception(f"Erro ao processar os dados: {e}")

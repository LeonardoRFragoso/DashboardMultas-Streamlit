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

            /* Estilo para o botão de detalhes */
            .detail-button {
                width: 100%;
                background-color: #F37529;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 10px;
            }

            /* Container do botão */
            .button-container {
                display: flex;
                justify-content: center;
                padding-top: 10px;
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

    # Cálculos dos indicadores
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
            data_consulta.strftime('%d/%m/%Y')
            if isinstance(data_consulta, pd.Timestamp) else str(data_consulta)
        )
    except (IndexError, KeyError):
        data_formatada = "N/A"

    # Renderizar indicadores sem os botões
    indicators_data = [
        ("Total de Multas", total_multas),
        ("Valor Total das Multas", f"R$ {valor_total_multas:,.2f}"),
        ("Multas no Ano Atual", multas_ano_atual),
        ("Valor Total Multas no Ano Atual", f"R$ {valor_multas_ano_atual:,.2f}"),
        ("Multas no Mês Atual", multas_mes_atual),
        ("Valor das Multas no Mês Atual", f"R$ {valor_multas_mes_atual:,.2f}"),
        ("Data da Consulta", data_formatada)
    ]

    # Renderizar os indicadores
    for i, (title, value) in enumerate(indicators_data):
        st.markdown(f"""
            <div class="indicador">
                <span>{title}</span>
                <p>{value}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Adicionar botão abaixo do indicador
        if st.button("🔍 Detalhes", key=f"detail_btn_{i}"):
            # Adicionar lógica específica para cada indicador
            if i == 0:  # Total de Multas
                st.dataframe(unique_fines)
            elif i == 1:  # Valor Total
                st.dataframe(unique_fines[[5, 14]])
            elif i == 2:  # Multas Ano Atual
                st.dataframe(unique_fines[unique_fines[9].dt.year == ano_atual])
            elif i == 3:  # Valor Ano Atual
                st.dataframe(unique_fines[unique_fines[9].dt.year == ano_atual][[5, 14]])
            elif i == 4:  # Multas Mês Atual
                st.dataframe(filtered_data[
                    (filtered_data[9].dt.year == ano_atual) & 
                    (filtered_data[9].dt.month == mes_atual)
                ])
            elif i == 5:  # Valor Mês Atual
                st.dataframe(filtered_data[
                    (filtered_data[9].dt.year == ano_atual) & 
                    (filtered_data[9].dt.month == mes_atual)
                ][[5, 14]])
            elif i == 6:  # Data Consulta
                st.write(f"Período: {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}")
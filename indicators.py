def render_indicators(data, filtered_data, data_inicio, data_fim):
    render_css()

    if 5 in data.columns:
        unique_fines = data.drop_duplicates(subset=[5])
    else:
        st.error("A coluna com índice 5 não foi encontrada nos dados.")
        unique_fines = pd.DataFrame(columns=[5, 14, 9])

    # Cálculos dos indicadores (mantido como estava)
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

    # HTML dos indicadores com os botões
    indicadores_html = f"""
    <div class="indicadores-container">
        <div class="indicador" data-id="total_multas">
            <span>Total de Multas</span>
            <p>{total_multas}</p>
        </div>
        <div class="indicador" data-id="valor_total">
            <span>Valor Total das Multas</span>
            <p>R$ {valor_total_multas:,.2f}</p>
        </div>
        <div class="indicador" data-id="multas_ano">
            <span>Multas no Ano Atual</span>
            <p>{multas_ano_atual}</p>
        </div>
        <div class="indicador" data-id="valor_ano">
            <span>Valor Total Multas no Ano Atual</span>
            <p>R$ {valor_multas_ano_atual:,.2f}</p>
        </div>
        <div class="indicador" data-id="multas_mes">
            <span>Multas no Mês Atual</span>
            <p>{multas_mes_atual}</p>
        </div>
        <div class="indicador" data-id="valor_mes">
            <span>Valor das Multas no Mês Atual</span>
            <p>R$ {valor_multas_mes_atual:,.2f}</p>
        </div>
        <div class="indicador" data-id="data_consulta">
            <span>Data da Consulta</span>
            <p>{data_formatada}</p>
        </div>
    </div>
    """

    # Renderizar os indicadores
    st.markdown(indicadores_html, unsafe_allow_html=True)

    # Botões de detalhes alinhados com os indicadores
    btn_col1, btn_col2, btn_col3, btn_col4, btn_col5, btn_col6, btn_col7 = st.columns(7)
    
    with btn_col1:
        if st.button("🔍 Detalhes", key="total_multas", type="primary"):
            st.dataframe(unique_fines)
    
    with btn_col2:
        if st.button("🔍 Detalhes", key="valor_total", type="primary"):
            st.dataframe(unique_fines[[5, 14]])

    with btn_col3:
        if st.button("🔍 Detalhes", key="multas_ano", type="primary"):
            st.dataframe(unique_fines[unique_fines[9].dt.year == ano_atual])
    
    with btn_col4:
        if st.button("🔍 Detalhes", key="valor_ano", type="primary"):
            st.dataframe(unique_fines[unique_fines[9].dt.year == ano_atual][[5, 14]])
    
    with btn_col5:
        if st.button("🔍 Detalhes", key="multas_mes", type="primary"):
            st.dataframe(filtered_data[
                (filtered_data[9].dt.year == ano_atual) & 
                (filtered_data[9].dt.month == mes_atual)
            ])
    
    with btn_col6:
        if st.button("🔍 Detalhes", key="valor_mes", type="primary"):
            st.dataframe(filtered_data[
                (filtered_data[9].dt.year == ano_atual) & 
                (filtered_data[9].dt.month == mes_atual)
            ][[5, 14]])
    
    with btn_col7:
        if st.button("🔍 Detalhes", key="data_consulta", type="primary"):
            st.write(f"Período: {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}")

    # Adicionar CSS para alinhar os botões
    st.markdown("""
        <style>
            .stButton {
                display: flex;
                justify-content: center;
                margin-top: -20px;
            }
            
            .stButton > button {
                background-color: #F37529 !important;
                color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)
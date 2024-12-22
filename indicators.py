def render_indicators(data, filtered_data, data_inicio, data_fim):
    render_css()

    if 5 in data.columns:
        unique_fines = data.drop_duplicates(subset=[5])
    else:
        st.error("A coluna com índice 5 não foi encontrada nos dados.")
        unique_fines = pd.DataFrame(columns=[5, 14, 9])

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

    # Container grid para os indicadores
    col1, col2, col3, col4 = st.columns(4)
    col5, col6, col7 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="indicador">
                <span>Total de Multas</span>
                <p>{}</p>
            </div>
        """.format(total_multas), unsafe_allow_html=True)
        if st.button("🔍 Detalhes", key="btn_total", type="primary"):
            st.dataframe(unique_fines)

    with col2:
        st.markdown("""
            <div class="indicador">
                <span>Valor Total das Multas</span>
                <p>R$ {:.2f}</p>
            </div>
        """.format(valor_total_multas), unsafe_allow_html=True)
        if st.button("🔍 Detalhes", key="btn_valor_total", type="primary"):
            st.dataframe(unique_fines[[5, 14]])

    with col3:
        st.markdown("""
            <div class="indicador">
                <span>Multas no Ano Atual</span>
                <p>{}</p>
            </div>
        """.format(multas_ano_atual), unsafe_allow_html=True)
        if st.button("🔍 Detalhes", key="btn_multas_ano", type="primary"):
            st.dataframe(unique_fines[unique_fines[9].dt.year == ano_atual])

    with col4:
        st.markdown("""
            <div class="indicador">
                <span>Valor Total Multas no Ano Atual</span>
                <p>R$ {:.2f}</p>
            </div>
        """.format(valor_multas_ano_atual), unsafe_allow_html=True)
        if st.button("🔍 Detalhes", key="btn_valor_ano", type="primary"):
            st.dataframe(unique_fines[unique_fines[9].dt.year == ano_atual][[5, 14]])

    with col5:
        st.markdown("""
            <div class="indicador">
                <span>Multas no Mês Atual</span>
                <p>{}</p>
            </div>
        """.format(multas_mes_atual), unsafe_allow_html=True)
        if st.button("🔍 Detalhes", key="btn_multas_mes", type="primary"):
            st.dataframe(filtered_data[
                (filtered_data[9].dt.year == ano_atual) & 
                (filtered_data[9].dt.month == mes_atual)
            ])

    with col6:
        st.markdown("""
            <div class="indicador">
                <span>Valor das Multas no Mês Atual</span>
                <p>R$ {:.2f}</p>
            </div>
        """.format(valor_multas_mes_atual), unsafe_allow_html=True)
        if st.button("🔍 Detalhes", key="btn_valor_mes", type="primary"):
            st.dataframe(filtered_data[
                (filtered_data[9].dt.year == ano_atual) & 
                (filtered_data[9].dt.month == mes_atual)
            ][[5, 14]])

    with col7:
        st.markdown("""
            <div class="indicador">
                <span>Data da Consulta</span>
                <p>{}</p>
            </div>
        """.format(data_formatada), unsafe_allow_html=True)
        if st.button("🔍 Detalhes", key="btn_data", type="primary"):
            st.write(f"Data inicial: {data_inicio}")
            st.write(f"Data final: {data_fim}")
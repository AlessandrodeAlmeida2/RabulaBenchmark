import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração inicial do Streamlit
st.set_page_config(layout="wide")
st.title("Brazilian Legal Knowledge Proficiency Benchmark")

with st.spinner("Carregando arquivos..."):
    # Carregar os dados (certifique-se de que o caminho está correto)
    try:
        df_scoreboard = pd.read_pickle("./data/scoreboard.pkl")
    except FileNotFoundError:
        st.error("Arquivo 'scoreboard.pkl' não encontrado. Verifique o caminho para o arquivo de dados.")
        st.stop()


st.write("Competence in language models within the Brazilian legal domain.")

# --- FILTROS ---
col1, col2, col3 = st.columns(3)
with col1:
    model_options = df_scoreboard["model"].unique().tolist()
    model = st.multiselect("Modelo", model_options, default=model_options)

with col2:
    area_options = df_scoreboard["evaluated_area"].unique().tolist()
    # Remove 'all' das opções de filtro para evitar confusão
    if 'all' in area_options:
        area_options.remove('all')
    area = st.multiselect("Área: ", area_options)

with col3:
    task_options = {
        'Multiple Choice': 'multiple_choice',
        'Legal Document Identification': 'legal_document_identification',
        'Legal Document Writing': 'legal_document_writing',
        'Discursive': 'discursive'
    }
    selected_task = st.selectbox("Tarefa:", list(task_options.keys()))
    task_key = task_options[selected_task]

# --- LÓGICA DA TABELA ---

# Filtrar o DataFrame
df_filtrado = df_scoreboard
if model:
    df_filtrado = df_filtrado[df_filtrado['model'].isin(model)]
if area:
    df_filtrado = df_filtrado[df_filtrado['evaluated_area'].isin(area)]

# MODIFICAÇÃO: Criar um DataFrame para a exibição que exclui a categoria 'all'
df_display = df_filtrado[df_filtrado['evaluated_area'] != 'all']


if df_display.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# Criar a tabela dinâmica (pivot) usando o dataframe sem 'all'
st.subheader(f"{selected_task}")
pivot_df = df_display.pivot_table(
    index='evaluated_area',
    columns='model',
    values=task_key,
    aggfunc='mean'
)

# --- CÁLCULO DE MÉDIAS E VITÓRIAS ---
avg_row = pd.Series(name='Média', dtype=float)
wins_row = pd.Series(name='Vitórias', dtype=int)
win_counts = pd.Series(0, index=pivot_df.columns, dtype=int)

# Lógica de vitórias: Itera nas linhas para contar apenas vitórias sem empate
if not pivot_df.empty and len(pivot_df.columns) > 1:
    for index, row in pivot_df.iterrows():
        max_val = row.max()
        # Conta vitória apenas se o valor máximo for único na linha (sem empates)
        if (row == max_val).sum() == 1:
            winner_model = row.idxmax()
            win_counts[winner_model] += 1

# Preencher as linhas de Média e Vitórias para cada modelo
for col_model in pivot_df.columns:
    # MODIFICAÇÃO: Calcula a média usando o dataframe sem 'all' para evitar contagem dupla
    model_avg = df_display[df_display['model'] == col_model][task_key].mean()
    avg_row[col_model] = model_avg if pd.notnull(model_avg) else 0
    wins_row[col_model] = win_counts.get(col_model, 0)

# Juntar as linhas de dados com as de Média e Vitórias
summary_df = pd.DataFrame([avg_row, wins_row])
final_df = pd.concat([pivot_df, summary_df])

# --- FORMATAÇÃO E ESTILIZAÇÃO ---

# Função para aplicar cores
def highlight_winner(s):
    if not pd.api.types.is_numeric_dtype(s):
        return [''] * len(s)
    
    max_val = s.max()
    
    if (s == max_val).sum() > 1:
        return [''] * len(s)
    else:
        is_max = s == max_val
        return ['color: #28a745' if v else 'color: #dc3545' for v in is_max]

# Aplicar a estilização
styled_df = final_df.style

# Aplicar coloração apenas nas linhas de dados (excluindo Média e Vitórias)
data_rows = final_df.index.difference(['Média', 'Vitórias'])
if len(final_df.columns) > 1:
    styled_df = styled_df.apply(highlight_winner, axis=1, subset=(data_rows, final_df.columns))

# MODIFICAÇÃO: Aplica formatação específica para a linha de Média e uma geral para as outras
format_dict_general = {col: "{:g}" for col in final_df.columns}
format_dict_media = {col: "{:.2f}" for col in final_df.columns}

styled_df = styled_df.format(format_dict_general, subset=(final_df.index.difference(['Média']), final_df.columns))
styled_df = styled_df.format(format_dict_media, subset=(pd.IndexSlice['Média'], final_df.columns))


# Exibir a tabela
st.dataframe(styled_df, use_container_width=True)
st.write("\n")

# --- GRÁFICO INTERATIVO COM PLOTLY ---
st.subheader(f"Desempenho por Área - {selected_task}")

# MODIFICAÇÃO: Agrupar dados para o gráfico usando o dataframe sem 'all'
df_agrupado = df_display.groupby(["evaluated_area", "model"], as_index=False)[task_key].mean()

if not df_agrupado.empty:
    # Criar o gráfico de barras interativo
    fig = px.bar(
        df_agrupado,
        x="evaluated_area",
        y=task_key,
        color="model",
        barmode="group",
        labels={
            "evaluated_area": "Área Avaliada",
            task_key: "Pontuação"
        }
    )
    
    # Atualizar o layout para melhorar a legibilidade
    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Pontuação",
        legend_title="Modelo",
        xaxis={'categoryorder':'total descending'},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Não há dados suficientes para gerar o gráfico.")
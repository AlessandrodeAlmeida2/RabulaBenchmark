import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuração inicial do Streamlit
st.set_page_config(layout="wide")
st.title("Brazilian Legal Knowledge Proficiency Benchmark")

with st.spinner("Carregando arquivos..."):
    df_scoreboard = pd.read_pickle("./data/scoreboard.pkl")

st.write("Competência de modelos de linguagem no domínio jurídico brasileiro.")

# Dividir os checkboxes em colunas
col1, col2, col3 = st.columns(3)

with col1:
    # Multiselect de modelos na primeira coluna
    model = st.multiselect("Modelo", df_scoreboard["model"].unique().tolist())

with col2:
    # Multiselect de áreas na segunda coluna
    area = st.multiselect("Área: ", df_scoreboard["evaluated_area"].unique().tolist())

with col3:
    # Dropdown para seleção de tarefas
    task_options = {
        'Multiple Choice': 'multiple_choice',
        'Legal Document Identification': 'legal_document_identification',
        'Legal Document Writing': 'legal_document_writing',
        'Discursive': 'discursive'
    }
    selected_task = st.selectbox("Tarefa:", list(task_options.keys()))
    task_key = task_options[selected_task]

# Filtrar o DataFrame para os filtros selecionados
df_filtrado = df_scoreboard

if model:
    df_filtrado = df_filtrado[df_filtrado['model'].isin(model)]

if area:
    df_filtrado = df_filtrado[df_filtrado['evaluated_area'].isin(area)]

# Criar uma tabela dinâmica com os modelos como colunas
st.subheader(f"{selected_task}")

# Pivotar a tabela para ter os modelos como colunas
pivot_df = df_filtrado.pivot_table(
    index='evaluated_area',
    columns='model',
    values=task_key,
    aggfunc='mean'
).round(2)

# Adicionar coluna de vencedor
if not pivot_df.empty and len(pivot_df.columns) > 1:
    pivot_df['Winner'] = pivot_df.idxmax(axis=1)

# Exibir a tabela
st.dataframe(pivot_df, use_container_width=True)
st.write("\n")

# Criar gráfico para a tarefa selecionada
st.subheader(f"Rabula - Competência em {selected_task}")
fig, ax = plt.subplots(figsize=(12, 6))

# Resolver duplicatas: agrupar por evaluated_area e model e calcular a média
df_agrupado = df_filtrado.groupby(["evaluated_area", "model"], as_index=False)[task_key].mean()

# Pivotar os dados para o gráfico
df_pivot = df_agrupado.pivot(index="evaluated_area", columns="model", values=task_key)

# Plotar o gráfico de barras
df_pivot.plot(kind="bar", ax=ax)

ax.set_title(f"Comparação por {selected_task}")
ax.set_xlabel("Área Avaliada")
ax.set_ylabel("Pontuação")
ax.legend(title="Modelo")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
st.pyplot(fig)

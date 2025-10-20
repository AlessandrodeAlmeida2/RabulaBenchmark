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
col1, col2 = st.columns(2)

with col1:
    # Multiselect de modelos na primeira coluna
    model = st.multiselect("Modelo", df_scoreboard["model"].unique().tolist())

with col2:
    # Multiselect de áreas na segunda coluna
    area = st.multiselect("Área: ", df_scoreboard["evaluated_area"].unique().tolist())

# Filtrar o DataFrame para os filtros selecionados
df_filtrado = df_scoreboard

if model:
    df_filtrado = df_filtrado.query('model == @model')

if area:
    df_filtrado = df_filtrado.query('evaluated_area == @area')

st.dataframe(df_filtrado, use_container_width=False)

# Criar gráficos
tasks = ["legal_document_identification", "legal_document_writing", "discursive"]

for task in tasks:
    st.subheader(f"Rabula- competency in  {task.replace('_',' ')}")
    fig, ax = plt.subplots(figsize=(10, 6))

    # Resolver duplicatas: agrupar por evaluated_area e model e calcular a média
    df_agrupado = df_filtrado.groupby(["evaluated_area", "model"], as_index=False)[task].mean()

    # Pivotar os dados para o gráfico
    df_pivot = df_agrupado.pivot(index="evaluated_area", columns="model", values=task)

    # Plotar o gráfico de barras
    df_pivot.plot(kind="bar", ax=ax)

    ax.set_title(f"Comparing by {task}")
    ax.set_xlabel("Evaluated Area")
    ax.set_ylabel("Score")
    ax.legend(title="Model")
    st.pyplot(fig)

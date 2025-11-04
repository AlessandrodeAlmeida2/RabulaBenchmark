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

# Debug: Verificar colunas e valores únicos
print("Colunas do DataFrame:", df_scoreboard.columns.tolist())
print("Modelos únicos:", df_scoreboard['model'].unique().tolist())
print("Valores únicos na coluna de tarefa:", df_scoreboard[task_key].unique())

# Calcular métricas para os cards
try:
    # Dados para o gpt-4o-mini
    gpt_data = df_scoreboard[df_scoreboard['model'] == 'gpt-4o-mini']
    gpt_avg = gpt_data[task_key].mean()
    gpt_avg = round(gpt_avg, 2) if pd.notnull(gpt_avg) else 0.0
    
    # Dados para o sabiazinho_3
    sabiazinho_data = df_scoreboard[df_scoreboard['model'] == 'sabiazinho_3']
    sabiazinho_avg = sabiazinho_data[task_key].mean()
    sabiazinho_avg = round(sabiazinho_avg, 2) if pd.notnull(sabiazinho_avg) else 0.0
    
    # Para debug
    print(f"Média gpt-4o-mini: {gpt_avg}")
    print(f"Média sabiazinho_3: {sabiazinho_avg}")
    
except Exception as e:
    print("Erro ao calcular médias:", str(e))
    gpt_avg = 0.0
    sabiazinho_avg = 0.0

# Contar vitórias por modelo
if not pivot_df.empty and 'Winner' in pivot_df.columns:
    win_counts = pivot_df['Winner'].value_counts().to_dict()
    gpt_wins = win_counts.get('gpt-4o-mini', 0)
    sabiazinho_wins = win_counts.get('sabiazinho_3', 0)
    
    # Para debug
    print(f"Vitórias gpt-4o-mini: {gpt_wins}")
    print(f"Vitórias sabiazinho_3: {sabiazinho_wins}")
else:
    gpt_wins = 0
    sabiazinho_wins = 0

# Criar 3 colunas para os cards
col1, col2, col3 = st.columns(3)

# Card 1: Média gpt-4o-mini
with col1:
    st.metric("Média gpt-4o-mini", f"{gpt_avg}")

# Card 2: Média Sabiazinho 3
with col2:
    st.metric("Média Sabiazinho 3", f"{sabiazinho_avg}")

# Card 3: Vitórias
with col3:
    st.markdown("Vitórias")
    st.markdown(f"<div style='font-size: 1.9em; margin-top: -17px;'><b>GPT-4o-mini: {gpt_wins} | Sabiazinho 3: {sabiazinho_wins}</div>", unsafe_allow_html=True)

# Adicionar espaço antes da tabela
st.write("\n")

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

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from folium.plugins import MarkerCluster
import plotly.express as px
import shutil
import gzip


# Carregar DataFrame excluindo valores nulos
df = pd.read_csv('NYC_Collisions.csv', na_values=[
                 '', 'NA', 'N/A', 'null', 'NaN'])

# Excluir linhas com valores nulos
df = df.dropna()

# Salvar DataFrame compactado usando gzip
df.to_csv('NYC_Collisions.csv.gz', compression='gzip', index=False)

# Carregar DataFrame compactado usando gzip
with gzip.open('NYC_Collisions.csv.gz', 'rb') as f_in:
    with open('NYC_Collisions.csv', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

# Carregar DataFrame
df = pd.read_csv('NYC_Collisions.csv')

# Configurar a página do Streamlit
st.set_page_config(page_title='Análise de Colisões em NYC', layout='wide')

# Carregando uma imagem
image_path = 'imagem.png'

# Adicionando a imagem ao topo do dashboard
st.image(image_path, use_column_width=True)

# Título do Dashboard
st.title('Dashboard de Análise de Colisões em NYC')

# Módulo 1: Análise Temporal
st.header('Análise Temporal das Colisões')

# Criar uma coluna de mês e ano
df['YearMonth'] = pd.to_datetime(df['Date']).dt.to_period('M')

# Análise de colisões por ano
st.subheader('Número de Colisões por Ano')
fig_year = plt.figure(figsize=(12, 6))
df['Year'] = pd.to_datetime(df['YearMonth'].dt.to_timestamp()).dt.year
ax = sns.countplot(x='Year', data=df, palette='viridis')
plt.title('Número de Colisões por Ano')

# Adicionar rótulos (labels) no topo das barras
for p in ax.patches:
    ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, 10), textcoords='offset points')

st.pyplot(fig_year)


# Adicionar um slider para escolher o ano
selected_year = st.slider('Selecione o Ano', min_value=int(
    df['YearMonth'].dt.year.min()), max_value=int(df['YearMonth'].dt.year.max()))

# Filtrar o DataFrame pelo ano selecionado
filtered_df = df[df['YearMonth'].dt.year == selected_year]

# Garantir que a coluna 'Date' seja do tipo datetime
filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])

# Criar coluna 'Month' com nomes dos meses
filtered_df['Month'] = filtered_df['Date'].dt.month_name(locale='English')

# Verificar se há dados para o ano selecionado
if not filtered_df.empty:
    # Análise de colisões por mês
    st.subheader(f'Número de Colisões por Mês em {selected_year}')
    fig_month = plt.figure(figsize=(12, 6))
    ax = sns.countplot(x='Month', data=filtered_df, palette='viridis', order=[
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ])
    plt.title(f'Número de Colisões por Mês em {selected_year}')
    plt.xticks(rotation=45)

    # Adicionar rótulos (labels) no topo das barras
    for p in ax.patches:
        ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 10), textcoords='offset points')

    st.pyplot(fig_month)
else:
    st.warning(f'Não há dados disponíveis para o ano {selected_year}.')

# Insights sobre a análise de colisões por mês
st.subheader('Insights - Colisões por Mês:')

st.write("A análise mostra uma maior distribuição do número de colisões nos meses correspondentes ao período do verão, nos EUA.\n"
         "Fonte: [EF - Estados Unidos](https://www.ef.com.br/guia-destinos/estados-unidos/clima/)")


# Módulo 2: Análise Geográfica
st.header('Análise Geográfica de Colisões')

# Mapa Interativo Geográfico usando Folium
st.subheader('Mapa Interativo de Colisões com Pessoas Feridas/Mortas')

# Criar um mapa centrado em Nova York
mapa = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

# Criar um cluster para os marcadores
marker_cluster = MarkerCluster().add_to(mapa)

# Adicionar marcadores para cada colisão com pessoas feridas ou mortas
for index, row in df.iterrows():
    if row['Persons Injured'] > 0:
        if not pd.isna(row['Latitude']) and not pd.isna(row['Longitude']):
            if row['Persons Killed'] > 0:
                color = 'black'
                popup_text = f"Mortos: {row['Persons Killed']}"
            else:
                color = 'red'
                popup_text = f"Feridos: {row['Persons Injured']}"

            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                icon=folium.Icon(color=color),
                popup=popup_text
            ).add_to(marker_cluster)

# Adicionar controle de camadas
folium.LayerControl().add_to(mapa)

# Salvar o mapa como HTML
mapa.save("mapa_interativo.html")

# Exibir o mapa interativo usando st.components.html()
with open("mapa_interativo.html", "r", encoding="utf-8") as f:
    mapa_html = f.read()
st.components.v1.html(mapa_html, width=700, height=500)

# Observação
st.subheader('Observação:')

st.write("A utilização de um Mapa Geográfico Interativo na Análise proporciona uma visualização dinâmica e intuitiva dos locais de colisões em Nova York. ")
st.write("Ao explorar o mapa, é possível identificar padrões espaciais e concentrar-se em áreas específicas que exigem maior atenção em termos de segurança viária. ")
st.write("Essa abordagem geoespacial oferece insights valiosos para a tomada de decisões informadas e a implementação de medidas preventivas. ")
st.write("A interatividade proporcionada pelo mapa permite uma exploração personalizada, promovendo uma compreensão mais aprofundada dos dados.")


# Módulo 3: Análise de Fatores Contribuintes
st.header('Análise de Fatores Contribuintes')

# Análise de fatores contribuintes
st.subheader('Top 10 Fatores Contribuintes para Colisões')
fig_factors = plt.figure(figsize=(14, 8))
top_factors = df['Contributing Factor'].value_counts().nlargest(
    10)  # Selecionar os top 10 fatores
sns.countplot(y='Contributing Factor', data=df,
              order=top_factors.index, palette='viridis')
plt.title('Top 10 Fatores Contribuintes para Colisões')
st.pyplot(fig_factors)

st.write("O principal motivo de acidentes no trânsito em todo o mundo é frequentemente atribuído à falta de atenção ao volante.")
st.write("Essa negligência pode resultar em colisões graves e, em muitos casos, pode ser evitada com práticas de direção mais conscientes.")
st.write("É crucial conscientizar os motoristas sobre a importância da atenção total durante a condução e promover ações para melhorar a segurança nas vias.")
st.write("Além disso, campanhas de conscientização e medidas educacionais desempenham um papel vital na redução de incidentes relacionados à distração no trânsito.")
st.write("Fonte: https://agenciabrasil.ebc.com.br/radioagencia-nacional/geral/audio/2022-03/estudo-aponta-que-distracao-causa-18-dos-acidentes-de-carro-no-mundo#:~:text=O%20estudo%20apontou%20que%2018,feridas%20por%20causa%20das%20distra%C3%A7%C3%B5es.")


# Módulo 4: Análise de Feridos e Mortos por Tipo de Veículo
st.header('Análise de Feridos e Mortos por Tipo de Veículo')

# Adicione botões para selecionar o ano
slider_key = 'year_slider'  # Defina uma chave única
selected_year = st.slider('Selecione o Ano', key=slider_key, min_value=int(
    df['Year'].min()), max_value=int(df['Year'].max()))

# Filtrar o DataFrame com base no ano selecionado
filtered_df = df[df['Year'] == selected_year]

# Análise de feridos e mortos por tipo de veículo
st.subheader(
    f'Número de Pessoas Feridas e Mortas por Tipo de Veículo em {selected_year}')

# Criar um DataFrame para gráfico de pizza
pie_df = pd.DataFrame({
    'Vehicle Type': filtered_df['Vehicle Type'],
    'Persons Injured': filtered_df['Persons Injured'],
    'Persons Killed': filtered_df['Persons Killed']
})

# Melt para transformar o DataFrame para o formato adequado para o gráfico de pizza
pie_df = pie_df.melt(id_vars='Vehicle Type',
                     var_name='Status', value_name='Count')

# Filtrar o DataFrame para incluir apenas dados maiores que zero
pie_df = pie_df[pie_df['Count'] > 0]

# Calcular os top 5 veículos com base no número total de feridos ou mortos
top_vehicles = pie_df.groupby('Vehicle Type')['Count'].sum().nlargest(5).index

# Filtrar o DataFrame para incluir apenas os top 5 veículos
pie_df = pie_df[pie_df['Vehicle Type'].isin(top_vehicles)]

# Criar gráfico de pizza interativo
fig_pie = px.pie(pie_df, values='Count', names='Vehicle Type',
                 title=f'Top 5 Veículos por Número de Pessoas Feridas e Mortas em {selected_year}')

# Adicionar rótulos diretamente no gráfico de pizza
fig_pie.update_traces(textinfo='percent+label')

# Adicionar botão de seleção de tipo (Injured/Killed)
status_selector = st.radio(
    "Selecione o Tipo", ('Persons Injured', 'Persons Killed'))

# Atualizar gráfico com base na seleção do tipo
filtered_pie_df = pie_df[pie_df['Status'] == status_selector]
fig_pie.update_traces(
    labels=filtered_pie_df['Vehicle Type'], selector=dict(type='pie'))

# Exibir gráfico de pizza
st.plotly_chart(fig_pie)


# Módulo 5: Análises Estatísticas
st.header('Análises Estatísticas dos Acidentes de Trânsito')

# Submódulo 1: Tendência Temporal por Hora de Acidentes de Trânsito
st.subheader('Tendência Temporal por Hora de Acidentes de Trânsito')

# Criar uma coluna de hora
df['Hour'] = pd.to_datetime(df['Time']).dt.hour

# Análise da distribuição temporal diária
st.subheader('Distribuição Temporal Diária de Colisões')

# Criar gráfico de distribuição horária
fig_hourly_distribution = plt.figure(figsize=(12, 6))
ax = sns.histplot(df['Hour'], bins=24, kde=False,
                  color='skyblue', edgecolor='black')
plt.title('Distribuição Temporal Diária de Colisões')
plt.xlabel('Hora do Dia')
plt.ylabel('Número de Colisões')
plt.xticks(range(24))  # Adicionar rótulos para cada hora

# Adicionar rótulos nas barras
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, 10), textcoords='offset points')

st.pyplot(fig_hourly_distribution)

st.write('De acordo com pesquisas, as aulas nos EUA geralmente encerram às 16h, seguidas pelo término do expediente de trabalho às 17h. Essa coincidência de horários levanta a questão se isso pode ser um fator contribuinte para o aumento de acidentes. A análise cuidadosa desse padrão pode fornecer insights valiosos sobre a possível relação entre os horários de término de aulas e trabalho e o aumento de incidentes no trânsito.')
st.write('Fonte: https://imigrefacil.com.br/post/carga-horaria-de-trabalho-nos-eua/',
         'https://super.abril.com.br/mundo-estranho/como-e-o-dia-a-dia-numa-escola-dos-eua')


st.header('AUTOR')


st.write('Este dashboard foi desenvolvido por NAYARA VALEVSKII, e tem como objetivo proporcionar uma análise interativa e informativa sobre acidentes de trânsito em Nova York, conforme proposto como Desafio do DataGlowUp do Heitor Sasaki. Caso tenha dúvidas, sugestões ou queira conhecer mais sobre meu trabalho, fique à vontade para entrar em contato através do meu Linkedin: https://www.linkedin.com/in/nayaraba/ ou verificar meus outros projetos no GitHub: https://github.com/NayaraWakewski. Agradeço pela contribuição!')

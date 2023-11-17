
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import folium
from folium.plugins import MarkerCluster
import plotly.express as px
import altair as alt
from PIL import Image

# Configurar a página do Streamlit primeiro
st.set_page_config(page_title='Análise de Colisões em NYC', layout='wide')


@st.cache_data
def gerar_df():
    df = pd.read_csv("NYC_Collisions.csv")
    return df


df = gerar_df()

# Título do Dashboard centralizado
st.markdown("<h1 style='text-align: center;'>Dashboard de Análise de Colisões em NYC</h1>",
            unsafe_allow_html=True)

# Tratando a coluna 'Date'
df['Date'] = pd.to_datetime(df['Date'])

# Excluindo linhas com valores nulos em qualquer coluna
df = df.dropna()


# Adicionando uma barra lateral (sidebar)
with st.sidebar:
    logo_teste = Image.open('imagem_cor.png')
    st.image(logo_teste, use_column_width=True)
    st.subheader('SELEÇÃO DE FILTROS')

    # Criando a seleção de anos
    anos_disponiveis = sorted(df['Date'].dt.year.unique(), reverse=True)
    # Adicionando a opção "Selecionar Todos"
    anos_disponiveis.insert(0, "Selecionar Todos")
    fAno = st.selectbox("Selecione o Ano:", options=anos_disponiveis)

    # Criando a seleção de meses
    meses_disponiveis = sorted(
        df[df['Date'].dt.year == fAno]['Date'].dt.month_name().unique(),
        key=lambda x: (pd.to_datetime(x, format='%B').month, x)
    )
    meses_disponiveis.insert(0, "Selecionar Todos")
    fMes = st.selectbox("Selecione o Mês:", options=meses_disponiveis)

    # Criando a seleção de bairros (Borough)
    bairros_disponiveis = sorted(df['Borough'].unique())
    bairros_disponiveis.insert(0, "Selecionar Todos")
    fBairro = st.selectbox("Selecione o Bairro:", options=bairros_disponiveis)

    # Criando a seleção de fatores de contribuição (Contributing Factor)
    fatores_disponiveis = sorted(df['Contributing Factor'].unique())
    fatores_disponiveis.insert(0, "Selecionar Todos")
    fFator = st.selectbox(
        "Selecione o Fator de Contribuição:", options=fatores_disponiveis)

    # Criando a seleção de tipos de veículos (Vehicle Type)
    tipos_veiculo_disponiveis = sorted(df['Vehicle Type'].unique())
    tipos_veiculo_disponiveis.insert(0, "Selecionar Todos")
    fTipoVeiculo = st.selectbox(
        "Selecione o Tipo de Veículo:", options=tipos_veiculo_disponiveis)

# Filtrando o DataFrame pelos filtros selecionados
df_filtrado = df[
    ((df['Date'].dt.year == fAno) | (fAno == "Selecionar Todos")) &
    ((df['Date'].dt.month_name() == fMes) | (fMes == "Selecionar Todos")) &
    ((df['Borough'] == fBairro) | (fBairro == "Selecionar Todos")) &
    ((df['Contributing Factor'] == fFator) | (fFator == "Selecionar Todos")) &
    ((df['Vehicle Type'] == fTipoVeiculo) |
     (fTipoVeiculo == "Selecionar Todos"))
]

# Verificando se há dados após a filtragem
if df_filtrado.empty:
    st.warning("Não há dados disponíveis com os filtros selecionados.")
else:
    # Exibindo o DataFrame filtrado
    st.markdown("<h3 style='text-align: center;'>Dados</h3>",
                unsafe_allow_html=True)
    st.dataframe(df_filtrado)
    st.markdown("Base de Dados dos Acidentes de Trânsito da Cidade de NY, disponibilizada por Heitor Sasaki, para o desafio DataGlowUp")

 # Adicionando um espaço com st.empty()
    st.empty()

    # Adicionando um título
    st.header('Análise Temporal das Colisões')

# Agrupando por ano e contando o número de colisões
grafico_colisoes = alt.Chart(df_filtrado).mark_bar().encode(
    x='year(Date):O',
    y='count():Q',
    color='year(Date):O',
    tooltip=['year(Date):O', 'count():Q']
).properties(
    width=800,
    height=400,
    title='Número de Colisões por Ano'
)

# Exibindo o gráfico
st.altair_chart(grafico_colisoes)

# Definindo uma paleta de cores rosa para os meses
cores_meses = alt.Color('month(Date):N', scale=alt.Scale(range=[
                        '#FFD1DF', '#FFA8C7', '#FF7FAF', '#FF5C99', '#FF407E', '#FF1F66', '#FF004C', '#D80036', '#AD0025', '#87001D', '#650016', '#44000F']))

# Agrupando por mês e contando o número de colisões
grafico_colisoes_mes = alt.Chart(df_filtrado).mark_bar().encode(
    x='count():Q',
    y=alt.Y('month(Date):O', title='Mês'),
    color=cores_meses,
    tooltip=['month(Date):O', 'count():Q']
).properties(
    width=800,
    height=400,
    title=f'Total de Colisões por Mês ({fAno})'
)

# Exibindo o gráfico
st.altair_chart(grafico_colisoes_mes)

# Insights sobre a análise de colisões por mês
st.markdown("Insights - Colisões por Mês:")
st.write("A análise mostra uma maior distribuição do número de colisões nos meses correspondentes ao período do verão, nos EUA.")
st.write(
    "Fonte: [EF - Estados Unidos](https://www.ef.com.br/guia-destinos/estados-unidos/clima/)")


# Módulo 2: Análise Geográfica
st.header('Análise Geográfica de Colisões')

# Mapa Interativo Geográfico usando Folium
st.subheader(
    f'Mapa Interativo de Colisões com Pessoas Feridas/Mortas ({fAno})')

# Criar um mapa centrado em Nova York
mapa = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

# Criar um cluster para os marcadores
marker_cluster = MarkerCluster().add_to(mapa)

# Adicionar marcadores para cada colisão com pessoas feridas ou mortas
for index, row in df_filtrado.iterrows():
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


# Análise de fatores contribuintes usando DataFrame filtrado
st.subheader('Top 10 Fatores Contribuintes para Colisões')

# Suponho que o DataFrame tenha colunas 'Contributing Factor' e 'Count'
df_filtrado2 = df_filtrado['Contributing Factor'].value_counts().nlargest(
    10).reset_index()
df_filtrado2.columns = ['Contributing Factor', 'Count']

# Criar gráfico de barras horizontais com Plotly Express
fig = px.bar(df_filtrado2, x='Count', y='Contributing Factor', orientation='h',
             labels={'Contributing Factor': 'Fatores Contribuintes',
                     'Count': 'Número de Colisões'},
             title='Fatores Contribuintes para Colisões',
             color='Count',  # Adicionar cor com base na contagem
             color_continuous_scale='Viridis',  # Escolher a escala de cores
             text='Count')  # Adicionar rótulos

# Adicionar interatividade
fig.update_layout(
    xaxis_title='Número de Colisões',
    yaxis_title='Fatores Contribuintes',
    # Ordenar categorias pelo total
    yaxis=dict(categoryorder='total ascending'),
)

# Exibir gráfico de barras horizontais interativo
st.plotly_chart(fig, use_container_width=True)

# Adicione outras informações ou análises que você desejar
st.write("O principal motivo de acidentes no trânsito em todo o mundo é frequentemente atribuído à falta de atenção ao volante.")
st.write("Essa negligência pode resultar em colisões graves e, em muitos casos, pode ser evitada com práticas de direção mais conscientes.")
st.write("É crucial conscientizar os motoristas sobre a importância da atenção total durante a condução e promover ações para melhorar a segurança nas vias.")
st.write("Além disso, campanhas de conscientização e medidas educacionais desempenham um papel vital na redução de incidentes relacionados à distração no trânsito.")
st.write("Fonte: [Agência Brasil](https://agenciabrasil.ebc.com.br/radioagencia-nacional/geral/audio/2022-03/estudo-aponta-que-distracao-causa-18-dos-acidentes-de-carro-no-mundo#:~:text=O%20estudo%20apontou%20que%2018,feridas%20por%20causa%20das%20distra%C3%A7%C3%B5es.)")


# Adicionando um título
st.header('Análise de Feridos e Mortos por Tipo de Veículo')

# Gráfico de barras interativo
bar_df = df_filtrado[['Vehicle Type', 'Persons Injured', 'Persons Killed',
                      'Pedestrians Injured', 'Pedestrians Killed', 'Cyclists Injured',
                      'Cyclists Killed', 'Motorists Injured', 'Motorists Killed']]

# Filtrar o DataFrame para incluir apenas dados maiores que zero
bar_df = bar_df[(bar_df['Persons Injured'] > 0) | (bar_df['Persons Killed'] > 0) |
                (bar_df['Pedestrians Injured'] > 0) | (bar_df['Pedestrians Killed'] > 0) |
                (bar_df['Cyclists Injured'] > 0) | (bar_df['Cyclists Killed'] > 0) |
                (bar_df['Motorists Injured'] > 0) | (bar_df['Motorists Killed'] > 0)]

# Criar gráfico de barras interativo com tamanho personalizado
fig_bar = px.bar(bar_df, x='Vehicle Type', y=['Persons Injured', 'Persons Killed',
                                              'Pedestrians Injured', 'Pedestrians Killed',
                                              'Cyclists Injured', 'Cyclists Killed',
                                              'Motorists Injured', 'Motorists Killed'],
                 title='Feridos e Mortos por Tipo de Veículo',
                 labels={'value': 'Count', 'variable': 'Status'},
                 height=600, width=900)  # Ajuste de altura e largura

# Adicionar rótulos diretamente no gráfico de barras
fig_bar.update_layout(barmode='stack', xaxis={
                      'categoryorder': 'total descending'})

# Exibir gráfico de barras
st.plotly_chart(fig_bar)

st.write('"Conforme indicado por estudos, a ausência do uso de cinto de segurança nos Estados Unidos está diretamente associada a um aumento significativo no número de fatalidades em acidentes de trânsito. A não adoção desse simples e crucial dispositivo de segurança resulta em consequências graves, impactando negativamente a segurança viária. É fundamental enfatizar a importância do uso do cinto de segurança como uma prática essencial para prevenir lesões graves e salvar vidas. Campanhas educativas e a conscientização contínua são essenciais para promover hábitos seguros no trânsito e reduzir o impacto negativo desses incidentes."')
st.write('Fonte: https://quatrorodas.abril.com.br/noticias/alerta-do-cinto-de-seguranca-pode-virar-problema-para-as-picapes-dos-eua/')

# Módulo 5: Análises Estatísticas
st.header('Análises Estatísticas dos Acidentes de Trânsito')

# Submódulo 1: Tendência Temporal por Hora de Acidentes de Trânsito
st.subheader('Distribuição Temporal Diária de Colisões')

# Criar uma coluna de hora no DataFrame filtrado
df_filtrado['Hour'] = pd.to_datetime(df_filtrado['Time']).dt.hour

# Criar gráfico de distribuição horária com base no DataFrame filtrado usando Altair
fig_hourly_distribution_altair = alt.Chart(df_filtrado).mark_bar().encode(
    x=alt.X('Hour:O', title='Hora do Dia', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('count():Q', title='Número de Colisões'),
    color=alt.Color('Hour:N', scale=alt.Scale(scheme='viridis')),
    tooltip=['Hour:N', 'count():Q']
).properties(
    width=800,  # Ajuste o tamanho conforme necessário
    height=400,
    title='Distribuição Temporal Diária de Colisões'
)

# Exibir gráfico de barras interativo usando Altair
st.altair_chart(fig_hourly_distribution_altair)

st.write('De acordo com pesquisas, as aulas nos EUA geralmente encerram às 16h, seguidas pelo término do expediente de trabalho às 17h. Essa coincidência de horários levanta a questão se isso pode ser um fator contribuinte para o aumento de acidentes. A análise cuidadosa desse padrão pode fornecer insights valiosos sobre a possível relação entre os horários de término de aulas e trabalho e o aumento de incidentes no trânsito.')
st.write('Fonte: https://imigrefacil.com.br/post/carga-horaria-de-trabalho-nos-eua/')
st.write('https://super.abril.com.br/mundo-estranho/como-e-o-dia-a-dia-numa-escola-dos-eua')


# Título da seção de autor com emoji de mulher morena no computador
st.header('AUTOR 🚀')

# Informações sobre o autor e o propósito do dashboard com emojis
st.write(
    '''
    Este dashboard foi desenvolvido por Nayara Valevskii com o objetivo de proporcionar uma análise interativa e informativa sobre acidentes de trânsito em Nova York, conforme proposto no Desafio do DataGlowUp por Heitor Sasaki.

    Caso tenha dúvidas, sugestões ou queira conhecer mais sobre meu trabalho, fique à vontade para entrar em contato através do meu [LinkedIn](https://www.linkedin.com/in/nayaraba/) ou verificar meus outros projetos no [GitHub](https://github.com/NayaraWakewski).

    Agradeço pela contribuição! 👩‍💻
    '''
)

# Adicione instruções de impressão ou st.write() para depuração
# st.write("Valores dos Filtros:")
# st.write(f"Ano: {fAno}, Mês: {fMes}, Bairro: {fBairro}, Fator de Contribuição: {fFator}, Tipo de Veículo: {fTipoVeiculo}")
# st.write(f"Número de linhas no DataFrame filtrado: {len(df_filtrado)}")


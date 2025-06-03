# CRIAR AMBIENTE VIRTUAL
# python -m venv maquininha

#ATIVAR AMBIENTE VIRTUAL
#CD maquininha\Scripts & call activate

#ATUALIZAR VERSAO PYTHON
#python.exe -m pip install --upgrade pip

#INSTALAR BIBLIOTECAS NECESSÁCIAS NO AMBIENTE VIRTUAL
#pip install -r ..\..\Scripts\requirements.txt

#EXECUTAR O STREAMLIT
#cd ..\.. & cd Scripts & streamlit run AP02.py
#streamlit run AP02.py

##LIBS ###########################################
##################################################
import streamlit as st
import pandas as pd
import plotly.express as px
import missingno as msno
import csv, os

##BASE ###########################################
##################################################
csv_file_path = os.path.join(current_dir, '..', 'basestratadas', 'filmes.csv')
df = pd.read_csv(csv_file_path, sep=';')


## TAMANHO DA TELA ###############################
#https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
##################################################
st.set_page_config(layout="wide")


## IMG DAS VARIAVEIS #############################
##################################################
img_nome = '🎬'
img_ano = '📅'
img_classificacao = '🔞'
img_duracao = '⏱️'
img_avaliacoes = '⭐'

## TITULO ########################################
#https://docs.streamlit.io/develop/api-reference/text
##################################################
st.markdown("<h1 style='text-align: center;'>TOP 250 🎬 FILMES - MAIS AVALIADOS</h1>", unsafe_allow_html=True)
st.write("Fonte: IMDB")
st.markdown("---")


## CARDS ########################################
#https://docs.streamlit.io/develop/api-reference/layout
#https://docs.streamlit.io/develop/api-reference/layout/st.columns
#https://docs.streamlit.io/develop/api-reference/data/st.metric
#################################################

with st.container(border=True):

    # Calcular totalizadores
    media_ano = df['Ano'].median()
    media_duracao = df['DuracaoN'].median()
    media_classificacao = df['Classificacao'].median()

    # Criar 3 colunas lado a lado
    col1, col2, col3 = st.columns(3)


    with col1:
        st.metric("📅 Média de Ano", f"{media_ano:.0f}")

    with col2:
        st.metric("⏱️ Duração Média", f"{media_duracao:.1f} min")

    with col3:
        st.metric("🔞 Média Classificação", f"{media_classificacao:.1f}")


## ANALISE UNIVARIADAS ############################
#https://docs.streamlit.io/develop/api-reference/layout/st.expander
#https://docs.streamlit.io/develop/api-reference/layout/st.container
#https://docs.streamlit.io/develop/api-reference/text
#https://docs.streamlit.io/develop/api-reference/widgets/st.selectbox
###################################################


with st.container(border=True):

    st.markdown(f"""## ℹ️ ANALISE RESUMO - UNIVARIADO""")

    variaveis = ['Ano', 'Classificacao', 'Nota', 'DuracaoN', 'AvaliaçoesN']
    variavel = st.selectbox("📊 Selecione o filtro:", variaveis)


    # Calcular estatísticas
    media = df[variavel].mean()
    mediana = df[variavel].median()
    minimo = df[variavel].min()
    maximo = df[variavel].max()
    desvio = df[variavel].std()

    # Contagem de ocorrências
    contagem = df[variavel].value_counts()
    mais_frequente = contagem.idxmax()
    max_freq = contagem.max()
    menos_frequente = contagem.idxmin()
    min_freq = contagem.min()


    col1, col2 = st.columns(2)
    with col1:
        st.markdown("---")
        st.markdown(f"<h4 style='text-align: center;'>🎬 HISTOGRAMA DE {variavel.upper()}</h4>", unsafe_allow_html=True)
        fig = px.histogram(df, x=variavel, text_auto=True)
        fig.update_traces(textposition='outside')
        fig.update_xaxes(tickmode='auto')        
        st.plotly_chart(fig)

    with col2:
        st.markdown("---")
        st.markdown(f"<h4 style='text-align: center;'>📦 BOXPLOT DE {variavel.upper()}</h4>", unsafe_allow_html=True)
        fig2 = px.box(df, x=variavel)
        fig2 = px.box(df, x=variavel, points="all")
        st.plotly_chart(fig2) 


    #RESUMOS
    st.subheader(f"Resumos de **{variavel}**:")
    st.write(
        f"O valor que mais se repete é **{mais_frequente}**, com {max_freq} ocorrência(s), "
        f"enquanto o valor menos frequente é **{menos_frequente}**, com apenas {min_freq} ocorrência(s).")
    st.write(f"A variável **{variavel}** possui média de {media:.0f}, com valores variando de {minimo:.0f} até {maximo:.0f}. A mediana é {mediana:.0f}, e o desvio padrão é {desvio:.0f}.")


st.markdown("---")

## ANALISE MULTIVARIADA ############################
###################################################

with st.container(border=True):

    st.markdown(f"""## ℹ️ ANALISE RESUMO - MULTIVARIADO""")

    variaveis = ['Ano', 'Classificacao', 'Nota', 'DuracaoN', 'AvaliaçoesN']
    selecionadas = st.multiselect(
        "📊 Selecione 2 a 3 variáveis (a terceira será usada como cor):",
        variaveis,
        default=['Classificacao', 'AvaliaçoesN']
    )

    if len(selecionadas) < 2 or len(selecionadas) > 3:
        st.warning("Por favor, selecione 2 ou 3 variáveis.")
        st.stop()

    var1, var2 = selecionadas[0], selecionadas[1]
    var_color = selecionadas[2] if len(selecionadas) == 3 else None

    # FORÇAR EIXO CATEGORICO 
    if var1 in ["Ano", "Classificacao", "Nota"]:
        df[var1] = df[var1].astype(str)

    st.markdown(f"<h4 style='text-align: center;'>📈 Análise de {var1.upper()} vs {var2.upper()}</h4>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        fig3 = px.scatter(df, x=var1, y=var2, color=var_color, color_continuous_scale="Hot_r")
        st.plotly_chart(fig3, use_container_width=True)
        

        fig7 = px.histogram(df, x=var1, color=var_color)
        st.plotly_chart(fig7, use_container_width=True)

    with col2:
        fig4 = px.box(df, x=var1, y=var2, color=var_color, points="all")
        st.plotly_chart(fig4, use_container_width=True)

        fig5 = px.violin(df, x=var1, y=var2, color=var_color,box=True, points="all")
        st.plotly_chart(fig5, use_container_width=True)



        # Calcular a correlação entre var1 e var2, se forem numéricas
    if pd.api.types.is_numeric_dtype(df[var1]) and pd.api.types.is_numeric_dtype(df[var2]):
        correlacao = df[[var1, var2]].corr().iloc[0, 1]

        # Interpretar a correlação
        if abs(correlacao) >= 0.3:
            interpretacao = "forte"
        elif abs(correlacao) >= 0.2:
            interpretacao = "moderada"
        elif abs(correlacao) >= 0.1:
            interpretacao = "fraca"
        else:
            interpretacao = "desprezível"

        sentido = "positiva" if correlacao > 0 else "negativa"

        st.markdown(
            f"📌 A correlação entre **{var1}** e **{var2}** é **{sentido}** e **{interpretacao}** "
            f"(*coeficiente: {correlacao:.2f}*)."
        )
    else:
        st.markdown(f"ℹ️ Não é possível calcular a correlação entre **{var1}** e **{var2}**, pois uma das variáveis não é numérica.")



    


## QUALIDADE DOS DADOS ############################
###################################################

with st.container(border=True):

    st.markdown(f"""## ℹ️ QUALIDADE DOS DADOS""")

    # Selecionar apenas variáveis numéricas
    variaveis_numericas = ['Ano', 'Classificacao', 'Nota', 'DuracaoN', 'AvaliaçoesN']
    df_num = df[variaveis_numericas]

    # Calcular a matriz de correlação
    correlacao = df_num.corr()


    col1, col2 = st.columns(2)
    with col1:
        # Plotar heatmap da correlação
        st.markdown("---")
        st.markdown(f"<h4 style='text-align: center;'>MATRIZ DE CORRELAÇÃO ENTRE VARIÁVEIS NUMÉRICAS</h4>", unsafe_allow_html=True)
        fig = px.imshow(correlacao, text_auto=True, color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
        fig.update_layout(title="🔗 Matriz de Correlação entre Variáveis Numéricas")
        st.plotly_chart(fig, use_container_width=True)


    with col2:
        #describe
        st.markdown("---")
        st.markdown(f"<h4 style='text-align: center;'>RESUMO DOS DADOS</h4>", unsafe_allow_html=True)
        st.dataframe(df.describe())


## ANALISE DE DADOS NULOS #########################
###################################################

with st.container(border=True):

    st.markdown(f"""## ℹ️ ANALISE DE DADOS NULO""")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("---")
        st.markdown(f"<h4 style='text-align: center;'>MAPA DE DADOS NULOS</h4>", unsafe_allow_html=True)
        vazios = msno.matrix(df)
        st.pyplot(vazios.figure)

    with col2:
        #EXIBE QUANTIDADE DE DADOS NULOS
        st.markdown("---")
        st.markdown(f"<h4 style='text-align: center;'>TABELA DOS DADOS NULOS</h4>", unsafe_allow_html=True)
        aux = df.isnull().sum().reset_index()
        aux.columns = ['variavel', 'qtd_miss']
        st.dataframe(aux)

    #RESUMOS
    st.subheader(f"Resumos de vazios:")
    st.write(f"Como houve tratamento nos dados não existe dados nulos")
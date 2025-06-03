#ATIVAR AMBIENTE VIRTUAL
#CD maquininha\Scripts & call activate

#EXECUTAR
#cd ..\.. & cd Scripts & python AP01.py

#Ctrl + Shift + P  Python: Select Interpreter

#//////////////////////////////////////////////////////////////////////////////////////
##IMPORTANDO AS BIBLIOTECAS
#//////////////////////////////////////////////////////////////////////////////////////
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import csv, os


#/////////////////////////////////////////////////////////////////////////////////////
#CHAMANDO NAVEGADOR E ABRINDO O SITE
#//////////////////////////////////////////////////////////////////////////////////////
navegador = webdriver.Chrome()
navegador.get('https://www.imdb.com/chart/top/?ref_=nv_mv_250')


#/////////////////////////////////////////////////////////////////////////////////////
# FUNÇÃO CRIADA PARA CONVERTER HORA-TEXTO EM DURAÇÃO E AVALIAÇOES TEXTO EM QUANTIDADE
#//////////////////////////////////////////////////////////////////////////////////////
def converter_valor(valor):
    valor = valor.replace('(', '').replace(')', '').replace('.', '').strip().lower()

    if 'mil' in valor:
        numero = float(valor.replace('mil', '').replace(',', '.')) * 1_000
    elif 'mi' in valor:
        numero = float(valor.replace('mi', '').replace(',', '.')) * 1_000_000
    else:
        numero = float(valor.replace(',', '.'))

    return numero

def converter_duracao(tempo_str):
    tempo_str = tempo_str.strip().lower()
    horas = 0
    minutos = 0

    if 'h' in tempo_str:
        partes = tempo_str.split('h')
        horas = int(partes[0].strip())
        if 'm' in partes[1]:
            minutos = int(partes[1].replace('m', '').strip())
    elif 'm' in tempo_str:
        minutos = int(tempo_str.replace('m', '').strip())

    return horas * 60 + minutos



#/////////////////////////////////////////////////////////////////////////////////////
# RASPAGEM E COLETA DOS DADOS DO SITE EM LISTAS
#//////////////////////////////////////////////////////////////////////////////////////
lista_nome = []
lista_ano = []
lista_nota = []
lista_classificacao = []
lista_avaliacao = []
lista_duracao = []

for sequencia in range(1, 251):
    nome = f'//*[@id="__next"]/main/div/div[3]/section/div/div[2]/div/ul/li[{sequencia}]/div/div/div/div/div[2]/div[1]/a/h3'
    ano = f'//*[@id="__next"]/main/div/div[3]/section/div/div[2]/div/ul/li[{sequencia}]/div/div/div/div/div[2]/div[2]/span[1]'
    nota = f'//*[@id="__next"]/main/div/div[3]/section/div/div[2]/div/ul/li[{sequencia}]/div/div/div/div/div[2]/span/div/span/span[1]'
    classificacao = f'//*[@id="__next"]/main/div/div[3]/section/div/div[2]/div/ul/li[{sequencia}]/div/div/div/div/div[2]/div[2]/span[3]'
    avaliacoes = f'//*[@id="__next"]/main/div/div[3]/section/div/div[2]/div/ul/li[{sequencia}]/div/div/div/div/div[2]/span/div/span/span[2]' 
    duracao = f'//*[@id="__next"]/main/div/div[3]/section/div/div[2]/div/ul/li[{sequencia}]/div/div/div/div/div[2]/div[2]/span[2]'

    nome_filme = navegador.find_element(By.XPATH, nome).text
    ano_filme = navegador.find_element(By.XPATH, ano).text
    nota_filme = navegador.find_element(By.XPATH, nota).text
    avaliacao_filme = navegador.find_element(By.XPATH, avaliacoes).text
    duracao_filme = navegador.find_element(By.XPATH, duracao).text

    classificacao_filme = navegador.find_elements(By.XPATH, classificacao)

    
    #TRATAMENTO DE VAZIO || INEXISTENTE
    if classificacao_filme:
        texto = classificacao_filme[0].text.strip()
        if texto.isnumeric():
            classificacao_filme = int(texto)
        else:
            classificacao_filme = 0  
    else:
        classificacao_filme = 0


    lista_nome.append(nome_filme)
    lista_ano.append(ano_filme)
    lista_nota.append(nota_filme)
    lista_classificacao.append(classificacao_filme)
    lista_avaliacao.append(avaliacao_filme)
    lista_duracao.append(duracao_filme)



#/////////////////////////////////////////////////////////////////////////////////////
# ARMAZEZANDO BASE ORIGINAL EM UM DATAFRAME
#//////////////////////////////////////////////////////////////////////////////////////
filmes_original = pd.DataFrame({
                        'Nome':lista_nome,
                        'Ano': lista_ano,
                        'Classificacao': lista_classificacao,
                        'Duracao': lista_duracao,
                        'Nota': lista_nota,
                        'Avaliaçoes': lista_avaliacao
                        })

filmes_original


#/////////////////////////////////////////////////////////////////////////////////////
# COPIANDO BASE ORIGINA PARA TRATAMENTO DOS DADOS
#//////////////////////////////////////////////////////////////////////////////////////
filmes_tratados = filmes_original.copy()

# TRATAMENTO SEPARAR O NUMERO DA SEQUENCIA DO NOME DO FILME 
filmes_tratados[['Numero', 'Nome']] = filmes_tratados['Nome'].str.split('. ', n=1, expand=True)


# TIPAGEM
filmes_tratados['Numero'] = filmes_tratados['Numero'].astype(int)
filmes_tratados['Ano'] = filmes_tratados['Ano'].astype(int)
filmes_tratados['Classificacao'] = filmes_tratados['Classificacao'].astype(int)
filmes_tratados['Nota'] = filmes_tratados['Nota'].str.replace(',', '.').astype(float)

# TRATAMENTO DE OUTLIER
#TRATAMENTO OUTLIER ANO 
ano_atual = datetime.now().year
filmes_tratados.loc[filmes_tratados['Ano'] < 1000, 'Ano'] = 99999
filmes_tratados.loc[filmes_tratados['Ano'] > ano_atual, 'Ano'] = ano_atual


#TRATAMENTO OUTLIER CLASSIFICAÇÃO
filmes_tratados.loc[filmes_tratados['Classificacao'] < 0, 'Classificacao'] = 99999
filmes_tratados.loc[filmes_tratados['Classificacao'] > 18, 'Classificacao'] = 18


#TRATAMENTO OUTLIER NOTAS
filmes_tratados.loc[filmes_tratados['Nota'] < 0, 'Nota'] = 99999
filmes_tratados.loc[filmes_tratados['Nota'] > 10, 'Nota'] = 10

#TRATAMENTO DURAÇÃO E QUANTIDADE DE AVALIAÇOES MANTENDO AS COLUNAS ORIGINAIS
filmes_tratados['DuracaoN'] = filmes_tratados['Duracao'].apply(converter_duracao)
filmes_tratados['AvaliaçoesN'] = filmes_tratados['Avaliaçoes'].apply(converter_valor)

#TRATAMENTO POSSIVEIS DADOS NULOS
filmes_tratados['Ano'] = filmes_tratados['Ano'].fillna(-3)
filmes_tratados['Classificacao'] = filmes_tratados['Classificacao'].fillna(-3)
filmes_tratados['Duracao'] = filmes_tratados['Duracao'].fillna(-3)
filmes_tratados['Nota'] = filmes_tratados['Nota'].fillna(-3)
filmes_tratados['Avaliaçoes'] = filmes_tratados['Avaliaçoes'].fillna(-3)


#REMOVER POSSIVEIS DUPLICIDADES
filmes_tratados.drop_duplicates(inplace=True)


#DATAFRAME TRATADO
filmes_tratados


#/////////////////////////////////////////////////////////////////////////////////////
# EXEMPLO DE UM DADOS AGRUPADOS - insights
#//////////////////////////////////////////////////////////////////////////////////////

resumo_por_classificacao_etaria = filmes_tratados.groupby('Classificacao').agg(
    filmes =  ('Classificacao', 'size'),
    Avaliacoes = ('AvaliaçoesN', 'sum'),
    mean_duracao = ('DuracaoN', 'mean')
    ).reset_index()

resumo_por_classificacao_etaria = resumo_por_classificacao_etaria.sort_values(by='filmes', ascending=False)

resumo_por_classificacao_etaria



#/////////////////////////////////////////////////////////////////////////////////////
# SALVANDO ARQUIVOS
#//////////////////////////////////////////////////////////////////////////////////////
# Criar pastas, se não existirem
os.makedirs('../basesoriginais', exist_ok=True)
os.makedirs('../basestratadas', exist_ok=True)
os.makedirs('../insights', exist_ok=True)

#SALVAR ARQUIVOS NAS RESPECTIVAS PASTAS
filmes_original.to_csv('../basesoriginais/filmes.csv', sep=';', index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
filmes_tratados.to_csv('../basestratadas/filmes.csv', sep=';', index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
resumo_por_classificacao_etaria.to_csv('../insights/idade.csv', sep=';', index=False)
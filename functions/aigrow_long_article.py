import openai
import json
import os
import time
import re
import pandas as pd
import streamlit as st
import requests

from dotenv import load_dotenv

load_dotenv()
from openai import AzureOpenAI

# gets the API Key from environment variable AZURE_OPENAI_API_KEY
#api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_key = os.getenv("AZURE_OPENAI_API_KEY_WPRAIZ")
client = AzureOpenAI(
    api_key=api_key,
    api_version="2023-12-01-preview",
    azure_endpoint="https://aigrow-swe.openai.azure.com/",
)   

from openai import OpenAI
    

class AIGrowDALLE:
    @staticmethod
    def gerar_prompt(prompt):
        response = client.completions.create(
            model="gpt-35-turbo-instruct",
            prompt=prompt,
            max_tokens=40,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        text = response.choices[0].text
        # transformar \n em <br> para quebrar linha no html
        #text = text.replace("\n", "<br>")
        # st.write(text)
        return text

    @staticmethod
    def gerar_imagem(prompt):
        client2 = OpenAI()
        response1 = client2.images.generate(
            model="Dalle3",
            prompt = prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        img1 = response1.data[0].url
        return img1

# Carregar variáveis do ambiente
def aigrow_azure_long_article(titulo_art):
    resp = []
    #url1 = "https://aigrow-content.azurewebsites.net/api/aig_long_article?code=2zPEHAjvSmcB7yveVLYJDDPwANoxCRDo84WCo69wNrG2AzFuMeZ3Ng=="
    url = "https://aigrow-content.azurewebsites.net/api/aig_mid_article?code=7wtRMFj5shOxGI64rteuykqZW6cJcMGHObWKc4Oz0bvLAzFuObS8kQ=="

    payload = json.dumps({
    "title": titulo_art,
    "user_email": "user@example.com",
    "user_id": "12345"
    })
    headers = {
    'Content-Type': 'application/json',
    'x-functions-key': 'SCWQk7rJWkpq-47YWhMqqhmpwYFMXwFOfnRp3zemAaGLAzFuiPdY0w=='
    }

    response = requests.request("POST", url, headers=headers, data=payload, stream=True)
    exemplo = response.text
    st.write(exemplo)
    st.write(response.text)


def gerar_artigo(titulo_art):
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1)
    usuario = "wpraiz"
    tempo_inicial = time.time()
    artigo = [] 
    lista_logs = []
    lista_h2s_full = []
    lista_tempos = []
    lista_tempos_gerar_texto = []
    
    def gerar_texto(prompt, max_tokens, temperature, i):
        tempo_texto = time.time() # Definir a variável tempo_texto antes de usá-la
        response = client.completions.create(
            model="gpt-35-turbo-instruct",
            prompt=prompt,
            max_tokens=2700,
            #max_tokens=222,
            temperature=0.9,
            top_p=1,
            frequency_penalty=0.2,
            presence_penalty=0.1            
        )
        text = response.choices[0].text
        # transformar \n em <br> para quebrar linha no html
        text = text.replace("\n", "<br>")
        tempo_texto_final = time.time()
        #  subtrai o tempo final do tempo inicial
        tempo_texto = tempo_texto_final - tempo_texto
        # transformar em string
        tempo_texto = str(tempo_texto)
        # adicionar na lista de tempos
        lista_tempos_gerar_texto.append(tempo_texto)
        tempo_texto = ""
        #st.write(text)
        st.markdown(text, unsafe_allow_html=True)
        return text


        # Função para gerar imagem
    def gerar_imagem(titulo):      
        prompt_dinamico = AIGrowDALLE.gerar_prompt(f"A partir do título: {titulo}, faça sugestões para o estilo, cores e elementos para a imagem do tipo thumbnail que irá representar o post, seja criativo e discreto ao mesmo tempo. \n\n")        
        img_01 = AIGrowDALLE.gerar_imagem(prompt_dinamico)
        return img_01
    

    def aigrow_titulos(prompt):
        response = client.completions.create(
            model="gpt-35-turbo-instruct",
            prompt=prompt,
            temperature=0.4,
            max_tokens=444,
            top_p=1,
            frequency_penalty=0.1,
            presence_penalty=0.3
        )        
        subtitles = response.choices[0].text
        subtitles = subtitles.split("\n") 
        subtitles = [x for x in subtitles if x != '']
        subtitles = [re.sub(r'^[#$\-\*\>\+\.:]+', '', x) for x in subtitles]
        subtitles = [re.sub(r'^\d+\.\s', '', x) for x in subtitles] # Remove 1. 2. 3. etc
        lista_h2s_full.append(subtitles) # Adiciona a lista de h2s
        subtitles = ["<h2>" + x + "</h2>" for x in subtitles] # Adiciona o h2 no inicio e no fim da string

        # Extrai informações necessárias da resposta antes de serializar
        save_log = {
            "id": response.id,
            "created": response.created,
            "subtitles": subtitles
        }

        response_log = json.dumps(save_log, indent=4)
        lista_logs.append(response_log)
        st.write(subtitles)
        return subtitles


    prompt_subtitulos = f" Gere 4 títulos do tipo H2 tomando como base que o título é " + titulo_art + " \n\n Utilize sua criatividade e evite repetições e redudância dos termos prinipai, variando os pronomes, verbos e claro, muita criatividade! \n\n "
    
    subtitulos = aigrow_titulos(prompt_subtitulos)
    subtitulo1 = str(subtitulos[0])
    subtitulo2 = str(subtitulos[1])
    subtitulo3 = str(subtitulos[2])
    subtitulo4 = str(subtitulos[3])

    subtitulos_clean = {
        "subtitulo1": lista_h2s_full[0][0],
        "subtitulo2": lista_h2s_full[0][1],
        "subtitulo3": lista_h2s_full[0][2],
        "subtitulo4": lista_h2s_full[0][3]
    }

    prompt_introducao = "Contexto: Introdução do Artigo. \n\n Objetivo: Criar uma introdução com aspecto de curiosidade para o leitor, use termos que gerem felicidade e surpresa ao leitor. \n\n Introdução ao Artigo falando sobre " + titulo_art + "  \n\n "
    st.markdown("<h2>Introdução</h2>", unsafe_allow_html=True)
    texto_introducao = gerar_texto(prompt_introducao, 500, 0.7, 0)

    # Gerar texto para o subtítulo 1
    st.markdown("<h2>" + subtitulo1 + "</h2>", unsafe_allow_html=True)
    prompt_subtitulo1 = "Gere um texto, com no mínimo 4 parágrafos, falando sobre o " + subtitulo1 + " interligando a ideia do texto com o tema principal que é " + titulo_art + "  \n\n "
    texto_subtitulo1 = gerar_texto(prompt_subtitulo1, 2500, 0.69, 1)

    # Gerar texto para o subtítulo 2
    st.markdown("<h2>" + subtitulo2 + "</h2>", unsafe_allow_html=True)
    prompt_subtitulo2 = "Sabendo que o título é " + titulo_art + " e o subtítulo anterior foi " + subtitulo1 + ", gere um texto falando sobre " + subtitulo2 + ", criando elementos que tenham conexão no início do texto com o subtítulo anterior e que no final tenham conectividade com o próximo contexto que é o " + subtitulo3 + " \n\n "
    texto_subtitulo2 = gerar_texto(prompt_subtitulo2, 1900, 0.7, 2)

    # Gerar texto para o subtítulo 3
    st.markdown("<h2>" + subtitulo3 + "</h2>", unsafe_allow_html=True)
    prompt_subtitulo3 = "Sabendo que o título é " + titulo_art + " e o subtítulo anterior foi " + subtitulo2 + ", gere um texto falando sobre " + subtitulo3 + ", criando elementos que tenham conexão no início do texto com o subtítulo anterior e que no final tenham conectividade com o próximo contexto que é o " + subtitulo4 + "  \n\n "
    texto_subtitulo3 = gerar_texto(prompt_subtitulo3, 1900, 0.7, 3)

    # Gerar texto para o subtítulo 4
    st.markdown("<h2>" + subtitulo4 + "</h2>", unsafe_allow_html=True)
    prompt_subtitulo4 = "Sabendo que o título é " + titulo_art + " e o subtítulo anterior foi " + subtitulo3 + ", gere um texto falando sobre " + subtitulo4 +", criando elementos que tenham conexão no início do texto com o subtítulo anterior e que no final gerem uma ideia de conclusão, muito embora o próximo contexto seja de fato um texto que ainda será criado para servir como conclusão.  \n\n "
    texto_subtitulo4 = gerar_texto(prompt_subtitulo4, 2900, 0.7, 4)

    # Conclusao
    response = client.completions.create(
        model="gpt-35-turbo-instruct",
        prompt= f" Título do artigo: {titulo_art}. \n\n Introdução: {texto_introducao}. \n\n Subtítulos: {subtitulo1} {subtitulo2} {subtitulo3} {subtitulo4}. \n\n Crie, no mínimo 4 parágrafos, longos, uma conclusão final para o artigo, utilizando elementos de ligação que possuam uma argumentação sequencial capaz de finalizar a ideia incial, média e final do artigo e do que está sendo proposto tomando como base a introdução, título e os subtitulos. \n\n Utilize a escrita na primeira pessoa para ser o mais próximo possível da realidade, início meio e fim da conclusão (é importante, finaliza,do por fim, toda via, concluindo, como falado, é sempre bom lembrar que, concluindo, obrigado por ler até aqui). \n\n Padrões para iniciar o texto, tais como : [esse foi, compartilhe conhecimento você também, planejar é viver, espero que tenha gostado, dúvidas? , continue ligado, gostou do Artigo?!, a conversa estava boa mas, vimos nesse artigo, concluindo, obrigado por estar conosco vimos neste artigo que, resumindo, concluindo, por fim, comentários finais, conclusão final]  ###  \n\n ",
        max_tokens=1200,
        temperature=0.9,
        top_p=1.0,
        frequency_penalty=0.2,
        presence_penalty=0.4
    )
    conclusao = response.choices[0].text
    # \n por <br>
    conclusao = conclusao.replace("\n", "<br>")
    # Vamos inserir, no início da conclusão, um <h3> Conclusão </h3>
    conclusao = "<br> <h3> Conclusão </h3> <br>" + "<p>" + conclusao + "</p>"
    
    # # Transformar todos os \n em <br> usando a funcao replace
    texto_introducao = texto_introducao.replace("\n", "<br>")

    # Vamos montar o artigo em uma só variável para utilizar no return
    art2_n = texto_introducao + subtitulo1 + texto_subtitulo1 + subtitulo2 + texto_subtitulo2 + subtitulo3 + texto_subtitulo3 + subtitulo4 + texto_subtitulo4 + conclusao
    art2_br = art2_n.replace("\n", "<br>") # \n por <br>

    # # Contar palavras em art2_n
    palavras = art2_n.split()
    qtd_palavras = len(palavras)

    # # Caracteres
    caracteres = len(art2_n)

    # # Contar parágrafos em art2_n
    paragrafos = art2_n.count("<br>")
    paragrafos = paragrafos + 1
    
    tempo_final = time.time()
    # str tempos
    tempo_inicial = str(tempo_inicial)
    tempo_final = str(tempo_final)

    #calcular
    tempo_total = float(tempo_final) - float(tempo_inicial)
    tempo_total = str(tempo_total)
    tempo_total = tempo_total.replace(".", ",")
    tempo_total = tempo_total + " segundos"

    #adicionar na lista
    lista_tempos.append(tempo_total)

    # artigo1 = art2_br
    titulo = titulo_art

    # # Gerar imagem
    #img_01, img_02 = gerar_imagem(titulo)

    artigo = {
        "titulo": titulo_art,
        "introducao": texto_introducao,
        "subtitulo1": subtitulo1,
        "texto_subtitulo1": texto_subtitulo1,
        "subtitulo2": subtitulo2,
        "texto_subtitulo2": texto_subtitulo2,
        "subtitulo3": subtitulo3,
        "texto_subtitulo3": texto_subtitulo3,
        "subtitulo4": subtitulo4,
        "texto_subtitulo4": texto_subtitulo4,
        "conclusao": conclusao,
        "artigoBR": art2_br,
        "artigoN": art2_n,
        "qtd_palavras": qtd_palavras,
        "caracteres": caracteres,
        "paragrafos": paragrafos,
        "com_tags": subtitulos,
        "lista_h2s_full": lista_h2s_full,
        "lista_logs": lista_logs,
        "tempo_total": tempo_total,
        "lista_tempos": lista_tempos,
        "lista_tempos_gerar_texto": lista_tempos_gerar_texto
        # "img_01": img_01,
        # "img_02": img_02        
    }

    return artigo
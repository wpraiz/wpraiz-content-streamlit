
import os
import re 
import json
import time
from dotenv import load_dotenv
import requests
from PIL import Image
from io import BytesIO
import streamlit as st
import pandas as pd
from function.aigrow_long_article import gerar_artigo, aigrow_azure_long_article, AIGrowDALLE

# Configuração da página do Streamlit
st.set_page_config(page_title="aiGrow Content Bulk Article Private Mode Staff", page_icon=":bookmark:")

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar conexão com o MongoDB
#ruri = os.getenv("MONGO_URI")
#client = MongoClient(uri, server_api=ServerApi('1'))

def download_and_show_image(image_url, image_name):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        # Abre a imagem a partir dos bytes recebidos
        image = Image.open(BytesIO(response.content))
        # Salva a imagem localmente
        image.save(f"{image_name}.png")
        # Exibe a imagem no Streamlit
        st.image(image, caption=image_name, use_column_width=True)
        return image
    else:
        st.error("Erro ao baixar a imagem")
        return None


# Função para obter dados do MongoDB
def get_data():
    db = client.aigrow
    items = db.aigc_new_articles.find()
    return list(items)

# Função para exibir o formulário de criação de artigo
def display_article_form():
    st.title("Gerador de Artigos com Inteligência Artificial (GPT-3 e GPT-4)")
    st.markdown(":heavy_check_mark: 100% gratuito")
    opcao_tipo_artigo = st.radio("Escolha o tipo de artigo", ["Artigo Longo", "Artigo Curto", "Azure Function"])
    titulo_artigo = st.text_input("Título do artigo", value="A Importância do Amor, Carinho, Respeito mútuo e Companheirismo no Relacionamento")
    if st.button("Gerar Artigo"):
        if opcao_tipo_artigo == "Artigo Longo":
            artigo = gerar_artigo(titulo_artigo)
            st.markdown(artigo['artigoBR'], unsafe_allow_html=True)
            st.image(artigo['img_01'], caption="Imagem 1")
            st.image(artigo['img_02'], caption="Imagem 2")
            #db.aigrow.aigc_new_articles.insert_one(artigo)
            st.success("Artigo gerado com sucesso!")
        elif opcao_tipo_artigo == "Artigo Curto":
            st.write("Funcionalidade ainda não implementada.")
        elif opcao_tipo_artigo == "Azure Function":
            artigo = aigrow_azure_long_article(titulo_artigo)
            st.markdown(artigo['artigoBR'], unsafe_allow_html=True)
           # db.aigrow.aigc_new_articles.insert_one(artigo)
            st.success("Artigo gerado com sucesso!")
    body = st.empty()
    with body:
        with st.container():
            st.title("Ações do aiGrow DALLE")

            texto_prompt_image = ""

            # Botão para gerar prompt
            if st.button("Gerar Prompt"):
                # Chame a função para gerar prompt
                texto_gerado = AIGrowDALLE.gerar_prompt(f"From the title, describe 3 styles keywords for the article: {titulo_artigo}, the result most be inline, like: <-item-1->, <-item-2->, <-item-3->")
                st.write(texto_gerado)

            # Botão para gerar imagem
            if st.button("Gerar Imagem"):
                # Chame a função para gerar imagem
                prompt_t1 = AIGrowDALLE.gerar_prompt(f"From the title, describe 3 styles keywords for the article: {titulo_artigo}, the result most be inline, like: <-item-1->, <-item-2->, <-item-3->")
                img_01 = AIGrowDALLE.gerar_imagem(f"Create a beautiful digital art thumbnail for blog with the title is {titulo_artigo} and the style is {prompt_t1}")
                
                img_name = re.sub(r"[^a-zA-Z0-9]+", ' ', titulo_artigo)
                img_name = img_name.replace(" ", "-")
                img_name = img_name.lower()
                img_01 = img_01.replace("data:image/png;base64,", "")
                img_01 = download_and_show_image(img_01, img_name)
                #img_01 = download_and_show_image(img_01, "Imagem 1")
                #st.image(img_02)

# Função para gerenciar artigos
def manage_articles():
    st.write("Puxando os artigos do MongoDB")
    items = get_data()
    df = pd.DataFrame(items)
    st.dataframe(df)

# Função para gerenciar sites
def manage_sites():
    st.write("Conteúdo da página Gerenciar Sites")

# Função para configurações
def settings():
    st.write("Conteúdo da página Configurações")

# Função para ferramentas de pandas
def tools_pandas():
    st.write("Conteúdo da página Tools - Pandas")
    from apps.Tools_Pandas import main as tools_pandas_main
    tools_pandas_main()

# Layout da sidebar
with st.sidebar:
    st.image('data/img/aigrow-logo-colored-transp.png', output_format='PNG', use_column_width=True)
    nav = st.radio("Navegação", ["Criar Artigo", "Gerenciar Artigos", "Gerenciar Sites", "Configurações", "MongoDB Gerenciamento", "Tools - Pandas"])
    st.markdown("---")
    st.markdown("### Sobre")
    st.info("Este aplicativo foi desenvolvido para auxiliar na criação de artigos para o aiGrow.")

# Exibição de conteúdo com base na navegação
if nav == "Criar Artigo":
    display_article_form()
elif nav == "Gerenciar Artigos":
    manage_articles()
elif nav == "Gerenciar Sites":
    manage_sites()
elif nav == "Configurações":
    settings()
elif nav == "Tools - Pandas":
    tools_pandas()
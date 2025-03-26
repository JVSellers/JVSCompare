import streamlit as st
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

st.set_page_config(page_title="Comparador de productos JVSellersCompany")
st.title("🛍️ Comparador de productos JVSellersCompany")

# Función para obtener datos de Amazon
def get_amazon_info(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")

    try:
        title = soup.find(id="productTitle").get_text().strip()
    except:
        title = "No encontrado"

    try:
        price = soup.find("span", class_="a-price-whole").get_text().strip()
    except:
        price = "No disponible"

    try:
        img = soup.find("img", id="landingImage")["src"]
    except:
        img = None

    return title, price, img

# Función para buscar en Alibaba
def search_alibaba(product_name):
    with DDGS() as ddgs:
        results = ddgs.text(product_name + " site:alibaba.com", max_results=3)
        for r in results:
            if "alibaba.com" in r["href"]:
                return r["href"]
    return None

# Función para obtener info de Alibaba
def get_alibaba_info(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")

    try:
        title = soup.find("h1").get_text().strip()
    except:
        title = "No encontrado"

    try:
        price = soup.find("span", class_="price").get_text().strip()
    except:
        price = "No disponible"

    try:
        img = soup.find("img")["src"]
        if not img.startswith("http"):
            img = "https:" + img
    except:
        img = None

    try:
        moq = soup.find(text=lambda t: "MOQ" in t).strip()
    except:
        moq = "No especificado"

    return title, price, moq, img

# Interfaz de usuario
amazon_url = st.text_input("Pega aquí el enlace del producto de Amazon")

if amazon_url:
    with st.spinner("Obteniendo datos de Amazon..."):
        a_title, a_price, a_img = get_amazon_info(amazon_url)
        st.subheader("🛍️ Amazon")
        st.write(f"**Nombre:** {a_title}")
        st.write(f"**Precio:** {a_price}")
        if a_img:
            st.image(a_img, width=250)
        st.write(f"[Ver en Amazon]({amazon_url})")

    with st.spinner("Buscando en Alibaba..."):
        ali_url = search_alibaba(a_title)
        if ali_url:
            ali_title, ali_price, ali_moq, ali_img = get_alibaba_info(ali_url)
            st.subheader("🌍 Alibaba")
            st.write(f"**Nombre:** {ali_title}")
            st.write(f"**Precio:** {ali_price}")
            st.write(f"**MOQ:** {ali_moq}")
            if ali_img:
                st.image(ali_img, width=250)
            st.write(f"[Ver en Alibaba]({ali_url})")
        else:
            st.warning("No se encontró el producto en Alibaba.")

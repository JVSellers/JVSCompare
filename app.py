import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

st.set_page_config(page_title="Comparador por imagen - JVSellersCompany")
st.title("🖼️ Comparador por imagen - JVSellersCompany")

# Función para obtener imagen desde Amazon
def get_amazon_image(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")
        img = soup.find("img", id="landingImage")["src"]
        return img
    except:
        return None

# Interfaz de usuario
amazon_url = st.text_input("Pega aquí el enlace del producto de Amazon")

if amazon_url:
    with st.spinner("Obteniendo imagen del producto de Amazon..."):
        img_url = get_amazon_image(amazon_url)
        if img_url:
            st.image(img_url, width=300)
            st.success("Imagen obtenida correctamente.")

            # Generar URL de búsqueda por imagen en Alibaba
            alibaba_search_url = f"https://www.alibaba.com/trade/search?imageUrl={quote(img_url)}&tab=all"
            st.markdown(f"### 🌍 [Haz clic aquí para ver la búsqueda por imagen en Alibaba]({alibaba_search_url})")
        else:
            st.error("No se pudo obtener la imagen del producto desde Amazon.")

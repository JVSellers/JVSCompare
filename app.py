import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from duckduckgo_search import DDGS

st.set_page_config(page_title="Comparador combinado - JVSellersCompany")
st.title("🛍️ Comparador combinado - JVSellersCompany")

# Función robusta para extraer título e imagen desde Amazon
def get_amazon_info(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")

        # Buscar título
        title_tag = soup.find("span", attrs={"id": "productTitle"})
        if not title_tag:
            title_tag = soup.find("span", class_="a-size-large product-title-word-break")
        title = title_tag.get_text().strip() if title_tag else None

        # Buscar imagen
        img_tag = soup.find("img", attrs={"id": "landingImage"})
        if not img_tag:
            img_tag = soup.find("img", class_="a-dynamic-image")
        img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else None

        return title, img_url
    except Exception as e:
        return None, None

# Función de búsqueda por texto en Alibaba usando DuckDuckGo
def search_alibaba_by_text(text_query):
    results = []
    try:
        with DDGS() as ddgs:
            query = f"{text_query} site:alibaba.com"
            search_results = ddgs.text(query, max_results=5)
            for r in search_results:
                if "alibaba.com" in r["href"]:
                    results.append({
                        "title": r["title"],
                        "link": r["href"],
                        "desc": r["body"]
                    })
    except Exception as e:
        st.error(f"Error buscando en DuckDuckGo: {e}")
    return results

# Interfaz
amazon_url = st.text_input("🔗 Pega aquí el enlace del producto de Amazon")

search_mode = st.radio("¿Cómo quieres buscar en Alibaba?", ["Buscar por texto (nombre)", "Buscar por imagen"])

if amazon_url:
    with st.spinner("Obteniendo información del producto en Amazon..."):
        title, img_url = get_amazon_info(amazon_url)

    if not title:
        st.error("❌ No se pudo obtener la información del producto.")
    else:
        st.subheader("📦 Producto en Amazon")
        st.write(f"**Nombre:** {title}")
        if img_url:
            st.image(img_url, width=250)
        st.write(f"[Ver en Amazon]({amazon_url})")

        if search_mode == "Buscar por texto (nombre)":
            st.subheader("🔍 Resultados de búsqueda por texto en Alibaba")
            results = search_alibaba_by_text(title)
            if results:
                for r in results:
                    st.markdown("---")
                    st.write(f"**Título:** {r['title']}")
                    st.write(f"**Descripción:** {r['desc']}")
                    st.write(f"[Ver en Alibaba]({r['link']})")
            else:
                st.warning("No se encontraron resultados por texto.")
        else:
            st.subheader("🖼️ Búsqueda por imagen en Alibaba")
            if img_url:
                alibaba_search_url = f"https://www.alibaba.com/trade/search?imageUrl={quote(img_url)}&tab=all"
                st.write(f"[Haz clic aquí para ver la búsqueda por imagen en Alibaba]({alibaba_search_url})")
                st.image(img_url, caption="Imagen usada para búsqueda", width=250)
            else:
                st.warning("No se pudo obtener la imagen del producto.")

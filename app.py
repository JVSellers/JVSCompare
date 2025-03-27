import streamlit as st
import requests
from urllib.parse import quote

SERPAPI_KEY = "b3696f2408535b9283c37b7755c7831166ce40ed9fadce67839da07cbe913d78"

st.set_page_config(page_title="Comparador con Google - JVSellersCompany")
st.title("🛒 Comparador de productos JVSellersCompany (Google + Amazon)")

query = st.text_input("🔍 Escribe un producto para buscar en Amazon usando Google")

def search_google_amazon(query):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": f"{query} site:amazon.es",
        "api_key": SERPAPI_KEY
    }
    res = requests.get(url, params=params)
    data = res.json()
    return data.get("shopping_results", [])

if query:
    with st.spinner("Buscando productos en Amazon vía Google..."):
        results = search_google_amazon(query)
        if results:
            st.subheader(f"🔎 Resultados para: {query}")
            for item in results:
                st.markdown("---")
                title = item.get("title", "Sin título")
                link = item.get("link", "#")
                price = item.get("price", "Precio no disponible")
                image = item.get("thumbnail")

                st.write(f"**{title}**")
                st.write(f"💰 {price}")
                if image:
                    # Generar búsqueda por imagen en Alibaba
                    alibaba_url = f"https://www.alibaba.com/trade/search?imageUrl={quote(image)}&tab=all"
                    st.image(image, width=200)
                    st.markdown(f"[🔎 Buscar por imagen en Alibaba]({alibaba_url})", unsafe_allow_html=True)
                st.write(f"[Ver en Amazon]({link})")
        else:
            st.warning("No se encontraron productos.")

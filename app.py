import streamlit as st
import requests
from urllib.parse import quote

SERPAPI_KEY = "b3696f2408535b9283c37b7755c7831166ce40ed9fadce67839da07cbe913d78"

st.set_page_config(page_title="Comparador JVSellersCompany")
st.image("logo.jpeg", width=250)
st.title("Comparador de productos JVSellersCompany")

query = st.text_input("🔍 Escribe un producto para buscar en Amazon (vía Google)")

def is_valid_amazon_link(url):
    return (
        "amazon." in url and
        "/dp/" in url or "/gp/product/" in url
    ) and "leer.amazon" not in url

def search_google_amazon(query):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": f"{query} site:amazon.es",
        "api_key": SERPAPI_KEY
    }
    res = requests.get(url, params=params)
    data = res.json()
    results = []
    if "shopping_results" in data:
        results.extend(data["shopping_results"])
    if "organic_results" in data:
        for r in data["organic_results"]:
            link = r.get("link", "")
            if is_valid_amazon_link(link):
                results.append({
                    "title": r.get("title"),
                    "link": link,
                    "thumbnail": r.get("thumbnail"),
                    "price": r.get("price", {}).get("extracted_value", "N/A")
                })
    return results

if query:
    with st.spinner("Buscando productos en Amazon..."):
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
                    alibaba_url = f"https://www.alibaba.com/trade/search?imageUrl={quote(image)}&tab=all"
                    st.image(image, width=200)
                    st.markdown(f"[🔎 Buscar por imagen en Alibaba]({alibaba_url})", unsafe_allow_html=True)
                st.write(f"[Ver en Amazon]({link})")
        else:
            st.warning("No se encontraron productos.")

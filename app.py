import streamlit as st
import requests
from urllib.parse import quote
from duckduckgo_search import DDGS

st.set_page_config(page_title="Comparador JVSellersCompany")
st.image("logo.jpeg", width=250)
st.title("Comparador de productos JVSellersCompany")

query = st.text_input("🔍 Escribe un producto para buscar en Amazon")

def search_amazon_duckduckgo(query):
    resultados = []
    with DDGS() as ddgs:
        q = f"{query} site:amazon.es"
        search = ddgs.text(q, max_results=10)
        for r in search:
            if "amazon.es" in r["href"]:
                resultados.append({
                    "title": r["title"],
                    "link": r["href"],
                    "body": r["body"],
                    "image": r.get("image", None)
                })
    return resultados

if query:
    with st.spinner("Buscando productos en Amazon..."):
        results = search_amazon_duckduckgo(query)
        if results:
            st.subheader(f"🔎 Resultados para: {query}")
            for r in results:
                st.markdown("---")
                st.write(f"**{r['title']}**")
                st.write(r["body"])
                if r["image"]:
                    st.image(r["image"], width=200)
                    alibaba_url = f"https://www.alibaba.com/trade/search?imageUrl={quote(r['image'])}&tab=all"
                    st.markdown(f"[🔎 Buscar por imagen en Alibaba]({alibaba_url})", unsafe_allow_html=True)
                st.write(f"[Ver en Amazon]({r['link']})")
        else:
            st.warning("No se encontraron productos.")

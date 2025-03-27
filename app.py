import streamlit as st
import requests
from urllib.parse import quote
from duckduckgo_search import DDGS

st.set_page_config(page_title="Comparador JVSellersCompany", layout="wide")
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
                st.markdown("----")
                col1, col2 = st.columns([1, 3])
                with col1:
                    if r["image"]:
                        st.image(r["image"], width=150)
                    else:
                        st.markdown("*Sin imagen disponible*")
                with col2:
                    st.markdown(f"### {r['title']}")
                    st.write(r["body"])
                    st.markdown(f"[🛒 Ver en Amazon]({r['link']})", unsafe_allow_html=True)

                    # Enlace a Alibaba
                    if r["image"]:
                        alibaba_url = f"https://www.alibaba.com/trade/search?imageUrl={quote(r['image'])}&tab=all"
                        st.markdown(f"[🖼️ Buscar por imagen en Alibaba]({alibaba_url})", unsafe_allow_html=True)
                    else:
                        alibaba_text_url = f"https://www.alibaba.com/trade/search?SearchText={quote(r['title'])}"
                        st.markdown(f"[🔤 Buscar por texto en Alibaba]({alibaba_text_url})", unsafe_allow_html=True)
        else:
            st.warning("No se encontraron productos.")

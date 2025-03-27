import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

st.set_page_config(page_title="Comparador JVSellersCompany")
st.image("logo.jpeg", width=250)
st.title("Comparador de productos JVSellersCompany")

query = st.text_input("🔍 Escribe un producto para buscar en Amazon")

def search_amazon_es(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    search_url = f"https://www.amazon.es/s?k={quote(query)}"
    res = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    results = []

    for div in soup.select("div.s-result-item[data-asin]"):
        asin = div["data-asin"]
        if not asin:
            continue
        title_tag = div.select_one("h2 span")
        link_tag = div.select_one("h2 a")
        image_tag = div.select_one("img")
        price_whole = div.select_one(".a-price-whole")
        price_frac = div.select_one(".a-price-fraction")

        title = title_tag.get_text().strip() if title_tag else "Sin título"
        link = f"https://www.amazon.es{link_tag['href']}" if link_tag else "#"
        image = image_tag["src"] if image_tag else None
        price = f"{price_whole.get_text()},{price_frac.get_text()} €" if price_whole and price_frac else "No disponible"

        results.append({
            "title": title,
            "link": link,
            "image": image,
            "price": price
        })
    return results

if query:
    with st.spinner("Buscando productos en Amazon..."):
        results = search_amazon_es(query)
        if results:
            st.subheader(f"🔎 Resultados para: {query}")
            for r in results:
                st.markdown("---")
                st.write(f"**{r['title']}**")
                st.write(f"💰 {r['price']}")
                if r["image"]:
                    alibaba_url = f"https://www.alibaba.com/trade/search?imageUrl={quote(r['image'])}&tab=all"
                    st.image(r["image"], width=200)
                    st.markdown(f"[🔎 Buscar por imagen en Alibaba]({alibaba_url})", unsafe_allow_html=True)
                st.write(f"[Ver en Amazon]({r['link']})")
        else:
            st.warning("No se encontraron productos.")

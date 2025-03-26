import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

st.set_page_config(page_title="Comparador por imagen - JVSellersCompany")
st.title("🖼️ Comparador por imagen - JVSellersCompany")

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
        img = soup.find("img", id="landingImage")["src"]
    except:
        img = None

    return title, img

# Función para obtener resultados desde búsqueda por imagen en Alibaba
from urllib.parse import quote

def get_alibaba_results_from_image(img_url):
    if not isinstance(img_url, str):
        img_url = img_url.decode('utf-8') if isinstance(img_url, bytes) else str(img_url)
    
    search_url = f"https://www.alibaba.com/trade/search?imageUrl={quote(img_url)}&tab=all"
    # ... rest of your code

    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")

    results = []
    for item in soup.select(".seb-supplier-card"):
        try:
            name = item.select_one(".title").get_text(strip=True)
            price = item.select_one(".price").get_text(strip=True)
            moq = item.select_one(".moq").get_text(strip=True)
            link = "https:" + item.select_one("a")["href"]
            image_tag = item.select_one("img")
            img = image_tag["src"] if image_tag and "src" in image_tag.attrs else None
            if img and not img.startswith("http"):
                img = "https:" + img
            results.append({
                "name": name,
                "price": price,
                "moq": moq,
                "link": link,
                "img": img
            })
        except:
            continue
    return search_url, results

# Interfaz de usuario
amazon_url = st.text_input("Pega aquí el enlace del producto de Amazon")

if amazon_url:
    with st.spinner("Obteniendo imagen del producto de Amazon..."):
        title, img_url = get_amazon_info(amazon_url)
        st.subheader("🛍️ Producto en Amazon")
        st.write(f"**Nombre:** {title}")
        if img_url:
            st.image(img_url, width=250)
        st.write(f"[Ver en Amazon]({amazon_url})")

    with st.spinner("Buscando productos similares en Alibaba por imagen..."):
        alibaba_url, results = get_alibaba_results_from_image(img_url)
        if results:
            st.subheader("🌍 Resultados en Alibaba")
            st.write(f"[Ver búsqueda completa en Alibaba]({alibaba_url})")
            for r in results:
                st.markdown("---")
                st.write(f"**Nombre:** {r['name']}")
                st.write(f"**Precio:** {r['price']}")
                st.write(f"**MOQ:** {r['moq']}")
                if r["img"]:
                    st.image(r["img"], width=200)
                st.write(f"[Ver producto]({r['link']})")
        else:
            st.warning("No se encontraron resultados con la imagen.")

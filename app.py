import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

st.set_page_config(page_title="Comparador Amazon vs Alibaba", layout="wide")
st.image("logo.jpeg", width=250)

st.title("Comparador Amazon vs Alibaba")

# -------- Funciones --------
def get_amazon_data(url_or_query):
    headers = {"User-Agent": "Mozilla/5.0"}
    if url_or_query.startswith("http"):
        url = url_or_query
    else:
        url = f"https://www.amazon.es/s?k={quote(url_or_query)}"

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")

    if "dp/" in url:
        title_tag = soup.find("span", id="productTitle")
        image_tag = soup.find("img", id="landingImage")
        price_tag = soup.find("span", class_="a-offscreen")
        return {
            "title": title_tag.get_text(strip=True) if title_tag else "Sin título",
            "image": image_tag["src"] if image_tag else None,
            "price": price_tag.get_text() if price_tag else "Sin precio",
            "link": url
        }
    else:
        first = soup.select_one("div.s-result-item[data-asin]")
        if not first:
            return None
        title = first.select_one("h2 span")
        image = first.select_one("img")
        price = first.select_one(".a-price .a-offscreen")
        link = first.select_one("h2 a")
        return {
            "title": title.get_text(strip=True) if title else "Sin título",
            "image": image["src"] if image else None,
            "price": price.get_text() if price else "Sin precio",
            "link": "https://www.amazon.es" + link["href"] if link else url
        }

def search_alibaba_by_text(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://www.alibaba.com/trade/search?SearchText={quote(query)}"
    res = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")

    results = []
    items = soup.select("div.list-no-v2-outter.J-offer-wrapper")
    for item in items[:3]:
        title = item.select_one(".elements-title-normal__outter a")
        price = item.select_one(".elements-offer-price-normal__price")
        img = item.select_one("img")
        link = title["href"] if title and title.has_attr("href") else None
        results.append({
            "title": title.get_text(strip=True) if title else "Sin título",
            "price": price.get_text(strip=True) if price else "Sin precio",
            "image": img["src"] if img and img.has_attr("src") else None,
            "link": link
        })
    return results

# -------- Interfaz --------
query = st.text_input("🔍 Pega un enlace de Amazon o escribe un producto")

if query:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🛒 Amazon")
        amazon_data = get_amazon_data(query)
        if amazon_data:
            st.write(f"**{amazon_data['title']}**")
            st.image(amazon_data["image"], width=200)
            st.write(f"💰 {amazon_data['price']}")
            st.markdown(f"[Ver en Amazon]({amazon_data['link']})")
        else:
            st.warning("No se pudo obtener información de Amazon.")

    with col2:
        st.markdown("### 🌍 Alibaba")
        results = search_alibaba_by_text(amazon_data["title"] if amazon_data else query)
        if results:
            for r in results:
                st.write(f"**{r['title']}**")
                st.image(r["image"], width=200)
                st.write(f"💰 {r['price']}")
                st.markdown(f"[Ver en Alibaba]({r['link']})")
                st.markdown("---")
        else:
            st.warning("No se encontraron resultados en Alibaba.")
 = f"https://www.amazon.es/s?k={quote(query)}"
    alibaba_url = f"https://www.alibaba.com/trade/search?SearchText={quote(query)}"

    amazon_img = generate_urlbox_image_url(amazon_url)
    alibaba_img = generate_urlbox_image_url(alibaba_url)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🌍 Alibaba")
        st.image(alibaba_img, use_column_width=True)
        st.markdown(f"[🔗 Ver en Alibaba]({alibaba_url})", unsafe_allow_html=True)

    with col2:
        st.markdown("### 🛒 Amazon")
        st.image(amazon_img, use_column_width=True)
        st.markdown(f"[🔗 Ver en Amazon]({amazon_url})", unsafe_allow_html=True)

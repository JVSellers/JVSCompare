import streamlit as st
from urllib.parse import quote

API_KEY = "7BFMDB6-ZTVMBK9-Q4CNZYG-8PSTBVP"

st.set_page_config(page_title="Comparador JVSellersCompany", layout="wide")
st.image("logo.jpeg", width=250)
st.title("")

query = st.text_input("", placeholder="Buscar producto...", label_visibility="collapsed")

def get_screenshot_url(target_url):
    return (
        f"https://shot.screenshotapi.net/screenshot"
        f"?token={API_KEY}"
        f"&url={quote(target_url)}"
        f"&output=image"
        f"&file_type=png"
        f"&wait_for_event=load"
        f"&delay=3"
        f"&full_page=true"
        f"&viewport=1920x2000"
    )

if query:
    amazon_url = f"https://www.amazon.es/s?k={quote(query)}"
    alibaba_url = f"https://www.alibaba.com/trade/search?SearchText={quote(query)}"

    amazon_img = get_screenshot_url(amazon_url)
    alibaba_img = get_screenshot_url(alibaba_url)

    st.subheader(f"🔍 Resultados para: {query}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🌍 Alibaba")
        st.image(alibaba_img, use_column_width=True)
        st.markdown(f"[Abrir búsqueda en Alibaba]({alibaba_url})", unsafe_allow_html=True)
    with col2:
        st.markdown("### 🛒 Amazon")
        st.image(amazon_img, use_column_width=True)
        st.markdown(f"[Abrir búsqueda en Amazon]({amazon_url})", unsafe_allow_html=True)

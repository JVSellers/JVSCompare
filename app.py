
import streamlit as st
from urllib.parse import quote, urlencode
import hashlib
import hmac

PUBLISHABLE_KEY = "EOw4BiqnFHKWAtnv"
SECRET_KEY = "150d3f30f34d487d8ba7d3af2824da85"

st.set_page_config(page_title="Comparador Amazon vs Alibaba", layout="wide")
st.image("logo.jpeg", width=250)
st.title("")

query = st.text_input("", placeholder="Buscar producto...", label_visibility="collapsed")

def generate_urlbox_image_url(target_url):
    options = {
        "url": target_url,
        "full_page": "true",
        "width": 1280,
        "height": 2000,
        "thumb_width": 600,
        "format": "png"
    }
    query_string = urlencode(sorted(options.items()))
    token = hmac.new(
        SECRET_KEY.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha1
    ).hexdigest()
    return f"https://api.urlbox.io/v1/{PUBLISHABLE_KEY}/{token}/png?{query_string}"

if query:
    st.subheader(f"🔍 Resultados para: {query}")

    amazon_url = f"https://www.amazon.es/s?k={quote(query)}"
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

import streamlit as st
from urllib.parse import quote
import streamlit.components.v1 as components

st.set_page_config(page_title="Comparador JVSellersCompany", layout="wide")
st.image("logo.jpeg", width=250)
st.title("Comparador de productos JVSellersCompany")

query = st.text_input("🔍 Escribe un producto para comparar")

if query:
    amazon_url = f"https://www.amazon.es/s?k={quote(query)}"
    alibaba_url = f"https://www.alibaba.com/trade/search?SearchText={quote(query)}"

    st.subheader("🔗 Accesos rápidos")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"[🛒 Ver búsqueda en Amazon]({amazon_url})", unsafe_allow_html=True)
    with col2:
        st.markdown(f"[🌍 Ver búsqueda en Alibaba]({alibaba_url})", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📊 Vista dividida (experimental)")
    colA, colB = st.columns(2)

    with colA:
        st.markdown("### 🌍 Alibaba")
        components.iframe(alibaba_url, height=600)

    with colB:
        st.markdown("### 🛒 Amazon")
        components.iframe(amazon_url, height=600)
        st.markdown(f"⚠️ Si no carga, abre [Amazon en nueva pestaña]({amazon_url})")

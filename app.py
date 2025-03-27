
import streamlit as st
import pandas as pd
from urllib.parse import quote, urlencode
import hashlib
import hmac

# Configuración de URLBox
PUBLISHABLE_KEY = "EOw4BiqnFHKWAtnv"
SECRET_KEY = "150d3f30f34d487d8ba7d3af2824da85"

# Setup
st.set_page_config(page_title="Comparador Amazon vs Alibaba", layout="wide")
st.title("")

# Estado inicial
if "comparaciones" not in st.session_state:
    st.session_state.comparaciones = []

# Entrada
query = st.text_input("", placeholder="Buscar producto...", label_visibility="collapsed")
precio_envio = st.number_input("💸 Coste estimado de envío por unidad (€)", value=2.0)
comision_amazon = st.number_input("📦 Comisión Amazon (% del precio)", value=15.0)

# Función para generar imagen desde URLBox
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

# Simulación de precios
def precio_amazon_ficticio(query):
    return 25.00

def precio_alibaba_ficticio(query):
    return 5.50, 100

# Lógica
if query:
    st.subheader(f"🔍 Resultados para: {query}")

    amazon_url = f"https://www.amazon.es/s?k={quote(query)}"
    alibaba_url = f"https://www.alibaba.com/trade/search?SearchText={quote(query)}"

    amazon_img = generate_urlbox_image_url(amazon_url)
    alibaba_img = generate_urlbox_image_url(alibaba_url)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🌍 Alibaba")
        st.image(alibaba_img, use_container_width=True)
        st.markdown(f"[🔗 Ver en Alibaba]({alibaba_url})", unsafe_allow_html=True)
    with col2:
        st.markdown("### 🛒 Amazon")
        st.image(amazon_img, use_container_width=True)
        st.markdown(f"[🔗 Ver en Amazon]({amazon_url})", unsafe_allow_html=True)

    st.markdown("---")

    # Simulaciones
    precio_amz = precio_amazon_ficticio(query)
    precio_ali, moq = precio_alibaba_ficticio(query)
    comision = precio_amz * comision_amazon / 100
    coste_total = precio_ali + precio_envio + comision
    margen = precio_amz - coste_total
    rentabilidad = (margen / coste_total) * 100 if coste_total > 0 else 0

    st.write(f"💰 Precio estimado en Amazon: {precio_amz} €")
    st.write(f"💰 Precio estimado en Alibaba: {precio_ali} € (MOQ: {moq})")
    st.write(f"📦 Comisión Amazon: {comision:.2f} €")
    st.write(f"🧾 Coste total estimado: {coste_total:.2f} €")
    st.write(f"📈 Margen estimado: {margen:.2f} € ({rentabilidad:.1f}%)")

    if st.button("➕ Añadir al estudio"):
        st.session_state.comparaciones.append({
            "Producto": query,
            "Precio Amazon (€)": precio_amz,
            "Precio Alibaba (€)": precio_ali,
            "MOQ": moq,
            "Precio Envío (€)": precio_envio,
            "Comisión Amazon (€)": round(comision, 2),
            "Margen (€)": round(margen, 2),
            "Rentabilidad (%)": round(rentabilidad, 1)
        })

# Mostrar tabla
if st.session_state.comparaciones:
    df = pd.DataFrame(st.session_state.comparaciones)
    st.subheader("📊 Comparaciones guardadas")
    st.dataframe(df, use_container_width=True)

    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Comparativa")
    st.download_button(
        label="📥 Descargar estudio en Excel",
        data=output.getvalue(),
        file_name="comparador_productos_jvsellers.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

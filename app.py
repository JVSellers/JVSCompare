import streamlit as st
import pandas as pd
from urllib.parse import quote

st.set_page_config(page_title="Comparador Amazon vs Alibaba", layout="wide")
st.image("logo.jpeg", width=250)
st.title("")

# Estado inicial
if "comparaciones" not in st.session_state:
    st.session_state.comparaciones = []

# Entrada
query = st.text_input("", placeholder="Buscar producto...", label_visibility="collapsed")
precio_envio = st.number_input("💸 Coste estimado de envío por unidad (€)", value=2.0)
comision_amazon = st.number_input("📦 Comisión Amazon (% del precio)", value=15.0)

# Simulación de precios
def precio_amazon_ficticio(query):
    return 25.00

def precio_alibaba_ficticio(query):
    return 5.50, 100

# Lógica
if query:
    st.subheader(f"🔍 Resultados para: {query}")

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
    st.subheader("📊 Comparaciones guardadas")
    df = pd.DataFrame(st.session_state.comparaciones)
    for idx, row in df.iterrows():
        st.write(f"**{row['Producto']}** - Precio Amazon: {row['Precio Amazon (€)']} € | Alibaba: {row['Precio Alibaba (€)']} € | Rentabilidad: {row['Rentabilidad (%)']}%")
        col1, _ = st.columns([1, 4])
        if col1.button(f"🗑️ Eliminar", key=f"del_{idx}"):
            st.session_state.comparaciones.pop(idx)
            st.experimental_rerun()

    st.markdown("---")
    if st.button("🧹 Limpiar todos los productos"):
        st.session_state.comparaciones.clear()
        st.experimental_rerun()

    df_final = pd.DataFrame(st.session_state.comparaciones)
    if not df_final.empty:
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_final.to_excel(writer, index=False, sheet_name="Comparativa")
        st.download_button(
            label="📥 Descargar estudio en Excel",
            data=output.getvalue(),
            file_name="comparador_productos_jvsellers.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

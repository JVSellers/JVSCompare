
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.hyperlink import Hyperlink

st.set_page_config(page_title="Amazon Product Loader", layout="wide")
st.image("logo.jpeg", width=120)
st.title("Amazon Product Loader - JVSellers")

st.markdown("### 1. Subir archivo Excel existente")
uploaded_file = st.file_uploader("Selecciona tu archivo Excel (.xlsm)", type=["xlsm"])

if "temp_table" not in st.session_state:
    st.session_state.temp_table = pd.DataFrame()

if uploaded_file:
    bytes_data = uploaded_file.read()
    wb = load_workbook(filename=BytesIO(bytes_data), data_only=True, keep_vba=True)
    sheet_alta = wb["Alta de productos"]
    sheet_calc = wb["calc. precio minimo intern"]

    df_alta = pd.DataFrame(sheet_alta.values)
    df_alta.columns = df_alta.iloc[0]
    df_alta = df_alta[1:]

    st.markdown("### Productos existentes:")
    st.dataframe(df_alta, use_container_width=True)

    st.markdown("---")
    st.markdown("### 2. Añadir nuevo producto desde URL de Amazon")
    url = st.text_input("Pega aquí la URL de Amazon")

    def obtener_info_amazon(url):
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")

            title = soup.find(id="productTitle")
            asin = url.split("/dp/")[1].split("/")[0] if "/dp/" in url else "N/A"
            price = soup.find("span", {"class": "a-price-whole"})
            prime = bool(soup.find("i", {"aria-label": "Amazon Prime"}))
            rating = soup.find("span", {"class": "a-icon-alt"})

            return {
                "Nombre del Articulo": title.get_text(strip=True) if title else "No encontrado",
                "ASIN": asin,
                "Precio": price.get_text(strip=True) if price else "No disponible",
                "PRIMEABLE": "Sí" if prime else "No",
                "Valoración": rating.get_text(strip=True) if rating else "N/A",
                "Url del producto": url
            }
        except Exception as e:
            return {"Error": str(e)}

    if st.button("Añadir producto"):
        if url:
            nuevo_producto = obtener_info_amazon(url)
            if "Error" not in nuevo_producto:
                st.session_state.temp_table = pd.concat(
                    [st.session_state.temp_table, pd.DataFrame([nuevo_producto])],
                    ignore_index=True
                )
            else:
                st.error("Error al obtener información: " + nuevo_producto["Error"])
        else:
            st.warning("Por favor, introduce una URL válida.")

    st.markdown("### Productos añadidos en esta sesión:")
    edited_table = st.data_editor(st.session_state.temp_table, use_container_width=True, num_rows="dynamic")
    st.session_state.temp_table = edited_table

    if st.button("Eliminar último producto"):
        if not st.session_state.temp_table.empty:
            st.session_state.temp_table = st.session_state.temp_table.iloc[:-1]

    st.markdown("---")
    if st.button("Descargar Excel actualizado"):
        for _, row in st.session_state.temp_table.iterrows():
            # Añadir a 'Alta de productos'
            sheet_alta.append([
                None, None, row.get("Nombre del Articulo"), row.get("Url del producto"),
                None, row.get("ASIN"), None, None, None, None, None, None, None, None,
                None, None, None, None, None, row.get("PRIMEABLE")
            ])

            # Añadir a 'calc. precio minimo intern'
            last_row = sheet_calc.max_row + 1
            sheet_calc.cell(row=last_row, column=1).value = row.get("Nombre del Articulo")
            sheet_calc.cell(row=last_row, column=2).value = "SI"
            sheet_calc.cell(row=last_row, column=1).hyperlink = row.get("Url del producto")

        output = BytesIO()
        wb.save(output)
        st.download_button("📥 Descargar archivo Excel", data=output.getvalue(), file_name="productos_actualizados.xlsm")

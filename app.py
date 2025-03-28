
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

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

    st.markdown("### Productos existentes:")
    data = list(sheet_alta.values)
    headers = data[0]
    df_alta = pd.DataFrame(data[1:], columns=headers)
    st.dataframe(df_alta, use_container_width=True)

    st.markdown("---")
    st.markdown("### 2. Añadir nuevo producto desde URL de Amazon")
    url = st.text_input("Pega aquí la URL de Amazon")

    def obtener_info_amazon(url):
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            title_tag = soup.select_one("#productTitle")
            title = title_tag.get_text(strip=True) if title_tag else "Nombre no encontrado"

            price_tag = soup.select_one("span.a-price > span.a-offscreen")
            price = price_tag.get_text(strip=True) if price_tag else "Precio no disponible"

            asin = None
            if "/dp/" in url:
                asin = url.split("/dp/")[1].split("/")[0]
            elif "asin=" in url:
                asin = url.split("asin=")[1].split("&")[0]

            prime = bool(soup.select_one("i[aria-label*='Prime']"))
            rating_tag = soup.select_one("span.a-icon-alt")
            rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"

            return {
                "Nombre del Articulo": title,
                "ASIN": asin,
                "Precio": price,
                "PRIMEABLE": "Sí" if prime else "No",
                "Valoración": rating,
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
        from openpyxl.utils import get_column_letter
        from openpyxl.cell.cell import Cell

        # Buscar el inicio real de la tabla en "Alta de productos"
        start_row_alta = 2
        for row_data in st.session_state.temp_table.itertuples(index=False):
            next_row = sheet_alta.max_row + 1
            cell = sheet_alta.cell(row=next_row, column=2)
            cell.value = row_data._asdict()["Nombre del Articulo"]
            cell.hyperlink = row_data._asdict()["Url del producto"]
            cell.style = "Hyperlink"

        # Añadir a "calc. precio minimo intern" en la columna A y B
        for row_data in st.session_state.temp_table.itertuples(index=False):
            next_row = sheet_calc.max_row + 1
            cell = sheet_calc.cell(row=next_row, column=1)
            cell.value = row_data._asdict()["Nombre del Articulo"]
            cell.hyperlink = row_data._asdict()["Url del producto"]
            cell.style = "Hyperlink"
            sheet_calc.cell(row=next_row, column=2).value = "SI"

        output = BytesIO()
        wb.save(output)
        st.download_button("📥 Descargar archivo Excel", data=output.getvalue(), file_name="productos_actualizados.xlsm")

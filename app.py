
import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table
from copy import copy
import os
from dotenv import load_dotenv
import re

load_dotenv()
API_KEY = os.getenv("RAINFOREST_API_KEY")

st.set_page_config(page_title="Amazon Product Loader - Rainforest API", layout="wide")
st.image("logo.jpeg", width=120)
st.title("Amazon Product Loader - JVSellers (Rainforest API)")

uploaded_file = st.file_uploader("Sube tu Excel (.xlsm)", type=["xlsm"])

if "temp_table" not in st.session_state:
    st.session_state.temp_table = pd.DataFrame()

def obtener_info_rainforest(asin):
    url = "https://api.rainforestapi.com/request"
    params = {
        "api_key": API_KEY,
        "type": "product",
        "amazon_domain": "amazon.es",
        "asin": asin
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        product = data.get("product", {})
        return {
            "Nombre del Articulo": product.get("title", "Nombre no encontrado"),
            "ASIN": asin,
            "Precio": product.get("buybox_winner", {}).get("price", {}).get("value", "Precio no disponible"),
            "PRIMEABLE": "Sí" if product.get("is_prime") else "No",
            "Valoración": product.get("rating", "N/A"),
            "Url del producto": product.get("link", "")
        }
    else:
        return {"Error": f"Error en la API: {response.status_code}"}

def extraer_asin_desde_url(url):
    match = re.search(r"/dp/([A-Z0-9]{10})", url)
    return match.group(1) if match else None

if uploaded_file:
    bytes_data = uploaded_file.read()
    wb = load_workbook(filename=BytesIO(bytes_data), data_only=False, keep_vba=True)
    sheet_alta = wb["Alta de productos"]
    sheet_calc = wb["calc. precio minimo intern"]

    st.markdown("### Añadir nuevo producto desde URL de Amazon")
    url = st.text_input("Pega aquí la URL de Amazon")

    if st.button("Añadir producto"):
        asin = extraer_asin_desde_url(url)
        if asin:
            nuevo = obtener_info_rainforest(asin)
            if "Error" not in nuevo:
                st.session_state.temp_table = pd.concat([st.session_state.temp_table, pd.DataFrame([nuevo])], ignore_index=True)
                st.success(f"Producto añadido con ASIN: {asin}")
            else:
                st.error(nuevo["Error"])
        else:
            st.warning("No se pudo extraer un ASIN válido de la URL.")

    st.dataframe(st.session_state.temp_table, use_container_width=True)

    if st.button("Eliminar último producto"):
        if not st.session_state.temp_table.empty:
            st.session_state.temp_table = st.session_state.temp_table.iloc[:-1]

    if st.button("Descargar Excel actualizado"):

        def clone_row(ws, row_idx):
            new_idx = row_idx + 1
            ws.insert_rows(new_idx)
            for col_idx, cell in enumerate(ws[row_idx], start=1):
                new_cell = ws.cell(row=new_idx, column=col_idx)
                new_cell.value = cell.value
                if cell.has_style:
                    new_cell._style = copy(cell._style)
                if cell.hyperlink:
                    new_cell.hyperlink = copy(cell.hyperlink)

        if sheet_alta._tables:
            table = list(sheet_alta._tables.values())[0]
            ref = table.ref
            start_col_letter = ref.split(":")[0][0]
            start_row = int(ref.split(":")[0][1:])
            end_col_letter = ref.split(":")[1][0]
            end_row = int(ref.split(":")[1][1:])
            new_end_row = end_row + len(st.session_state.temp_table)
            table.ref = f"{start_col_letter}{start_row}:{end_col_letter}{new_end_row}"

        row_alta = sheet_alta.max_row
        row_calc = sheet_calc.max_row

        for _, row in st.session_state.temp_table.iterrows():
            clone_row(sheet_alta, row_alta)
            row_alta += 1
            sheet_alta.cell(row=row_alta, column=2).value = row["Nombre del Articulo"]
            sheet_alta.cell(row=row_alta, column=2).hyperlink = row["Url del producto"]
            sheet_alta.cell(row=row_alta, column=2).style = "Hyperlink"

            clone_row(sheet_calc, row_calc)
            row_calc += 1
            sheet_calc.cell(row=row_calc, column=1).value = row["Nombre del Articulo"]
            sheet_calc.cell(row=row_calc, column=1).hyperlink = row["Url del producto"]
            sheet_calc.cell(row=row_calc, column=1).style = "Hyperlink"
            sheet_calc.cell(row=row_calc, column=2).value = "SI"
            if isinstance(row["Precio"], (int, float)):
                sheet_calc.cell(row=row_calc, column=3).value = row["Precio"]

        output = BytesIO()
        wb.save(output)
        st.download_button("📥 Descargar Excel", data=output.getvalue(), file_name="productos_actualizados.xlsm")

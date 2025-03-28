
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table
from copy import copy
import re

st.set_page_config(page_title="Amazon Product Loader", layout="wide")
st.image("logo.jpeg", width=120)
st.title("Amazon Product Loader - JVSellers")

uploaded_file = st.file_uploader("Sube tu Excel (.xlsm)", type=["xlsm"])

if "temp_table" not in st.session_state:
    st.session_state.temp_table = pd.DataFrame()

if uploaded_file:
    bytes_data = uploaded_file.read()
    wb = load_workbook(filename=BytesIO(bytes_data), data_only=False, keep_vba=True)
    sheet_alta = wb["Alta de productos"]
    sheet_calc = wb["calc. precio minimo intern"]

    st.markdown("### Añadir nuevo producto desde Amazon")
    url = st.text_input("Pega aquí la URL del producto")

    def extraer_precio(soup):
        selectores = [
            "span.a-price > span.a-offscreen",
            "#price_inside_buybox",
            "#corePriceDisplay_desktop_feature_div span.a-offscreen",
            "#priceblock_ourprice",
            "#priceblock_dealprice"
        ]
        for selector in selectores:
            tag = soup.select_one(selector)
            if tag:
                return tag.get_text(strip=True)

        # Si no encuentra en los selectores estándar, intentar con .a-price-whole y .a-price-fraction
        whole = soup.select_one(".a-price-whole")
        fraction = soup.select_one(".a-price-fraction")
        if whole and fraction:
            return f"{whole.get_text(strip=True)}.{fraction.get_text(strip=True)}"
        return None

    def obtener_info_amazon(url):
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            title_tag = soup.select_one("#productTitle")
            title = title_tag.get_text(strip=True) if title_tag else "Nombre no encontrado"

            price_text = extraer_precio(soup)
            price_float = None
            if price_text:
                price_clean = price_text.replace("€", "").replace(",", ".").replace(u'\xa0', '').strip()
                try:
                    price_float = float(price_clean)
                except:
                    price_float = None

            asin = None
            if "/dp/" in url:
                asin = url.split("/dp/")[1].split("?")[0].split("/")[0]
            elif "asin=" in url:
                asin = url.split("asin=")[1].split("&")[0].split("/")[0]

            prime = bool(soup.select_one("i[aria-label*='Prime']"))
            rating_tag = soup.select_one("span.a-icon-alt")
            rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"

            return {
                "Nombre del Articulo": title,
                "ASIN": asin,
                "Precio": price_float if price_float is not None else "Precio no disponible",
                "PRIMEABLE": "Sí" if prime else "No",
                "Valoración": rating,
                "Url del producto": url
            }
        except Exception as e:
            return {"Error": str(e)}

    if st.button("Añadir producto"):
        if url:
            nuevo = obtener_info_amazon(url)
            if "Error" not in nuevo:
                st.session_state.temp_table = pd.concat([st.session_state.temp_table, pd.DataFrame([nuevo])], ignore_index=True)
                st.success("Producto añadido a la tabla temporal")
            else:
                st.error("Error: " + nuevo["Error"])

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

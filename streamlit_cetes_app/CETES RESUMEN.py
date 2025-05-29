import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import os

# Configuraciones iniciales
st.set_page_config(layout="wide")
st.title("📈 Análisis de CETES y Tipo de Cambio")
st.markdown("Esta app genera visualizaciones automáticas usando datos de Banxico y recursos embebidos.")

# Fechas
hoy = datetime.today()
inicio = hoy - timedelta(days=365)
fin = hoy

# Ruta de la fuente personalizada (asegúrate de subirla a 'assets/Lato-Bold.ttf')
font_path = os.path.join("assets", "Lato-Bold.ttf")

def cargar_fuente(nombre_archivo, tamano):
    path = os.path.join("assets", nombre_archivo)
    if os.path.exists(path):
        return ImageFont.truetype(path, tamano)
    return ImageFont.load_default()

# Fuentes
title_font = cargar_fuente("Lato-Bold.ttf", 90)
label_font = cargar_fuente("Lato-Bold.ttf", 70)
value_font = cargar_fuente("Lato-Bold.ttf", 65)
small_font = cargar_fuente("Lato-Bold.ttf", 40)
tiny_font = cargar_fuente("Lato-Bold.ttf", 35)

# Constantes Banxico
TOKEN = "1440756de925e6f19ce08bd468d397923d94430ac3480c33386a74a4f1dd94e0"
HEADERS = {"Bmx-Token": TOKEN}
BASE_URL = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/{}/datos/{}/{}"
SERIES = {
    "28 Días": "SF43936",
    "91 Días": "SF43939",
    "182 Días": "SF43942",
    "364 Días": "SF43945",
    "728 Días": "SF349785",
    "Tasa Objetivo": "SF61745",
    "Tipo de Cambio FIX": "SF43718"
}

@st.cache_data
def obtener_serie(clave, ini, fin):
    url = BASE_URL.format(clave, ini.strftime("%Y-%m-%d"), fin.strftime("%Y-%m-%d"))
    try:
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        datos = r.json()["bmx"]["series"][0]["datos"]
        df = pd.DataFrame(datos)
        df["fecha"] = pd.to_datetime(df["fecha"], dayfirst=True)
        df["dato"] = pd.to_numeric(df["dato"].str.replace(",", ""), errors="coerce")
        return df.dropna().sort_values("fecha")
    except Exception as e:
        st.warning(f"No se pudo obtener la serie {clave}: {e}")
        return pd.DataFrame()

resumen_series = {}
series_largas = {}

for nombre, clave in SERIES.items():
    df = obtener_serie(clave, inicio, fin)
    if not df.empty and len(df) >= 2:
        if nombre != "Tipo de Cambio FIX":
            resumen_series[nombre] = {
                "anterior": df["dato"].iloc[-2],
                "actual": df["dato"].iloc[-1]
            }
        series_largas[nombre] = df.set_index("fecha").resample("D").interpolate().reset_index()

def generar_resumen_cetes():
    img = Image.new("RGB", (1080, 1350), "white")
    draw = ImageDraw.Draw(img)
    for y in range(1350):
        r = int(173 + (255 - 173) * y / 1350)
        g = int(216 + (255 - 216) * y / 1350)
        b = int(230 + (255 - 230) * y / 1350)
        draw.line([(0, y), (1080, y)], fill=(r, g, b))

    draw.text((40, 40), "Resumen CETES", fill="#222222", font=title_font)

    y_pos = 180
    for plazo in ["28 Días", "91 Días", "182 Días", "364 Días", "728 Días"]:
        datos = resumen_series.get(plazo)
        if datos:
            draw.text((60, y_pos), plazo, fill="#D32F2F", font=label_font)
            draw.text((500, y_pos), f"Actual: {datos['actual']:.2f}%", fill="black", font=value_font)
            draw.text((500, y_pos + 70), f"Anterior: {datos['anterior']:.2f}%", fill="#555555", font=tiny_font)
            y_pos += 180

    tasa_obj = resumen_series.get("Tasa Objetivo", {"actual": 0, "anterior": 0})
    draw.multiline_text((60, y_pos + 10), "Tasa\nObjetivo", fill="#D32F2F", font=label_font, spacing=10)
    draw.text((500, y_pos + 10), f"Actual: {tasa_obj['actual']:.2f}%", fill="black", font=value_font)
    draw.text((500, y_pos + 80), f"Anterior: {tasa_obj['anterior']:.2f}%", fill="#555555", font=tiny_font)

    img.save("resumen_cetes.png")
    return img

# Generar y mostrar
imagen = generar_resumen_cetes()
st.image(imagen, caption="Resumen visual de tasas CETES", use_column_width=True)
st.success("✅ Imagen generada correctamente.")


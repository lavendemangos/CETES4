import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
from io import BytesIO
import zipfile
import os

# ---------- CONFIG ----------
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

# ---------- RUTAS ABSOLUTAS ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(BASE_DIR, "assets", "hucha.png")
font_zip_path = os.path.join(BASE_DIR, "assets", "lato.zip")

# ---------- STREAMLIT UI ----------
st.set_page_config(layout="wide")
st.title("📈 Análisis de CETES y Tipo de Cambio")
st.markdown("Esta app genera visualizaciones automáticas usando datos de Banxico y recursos embebidos.")

# Fecha fija de análisis (últimos 365 días)
today = datetime.today()
inicio = today - timedelta(days=365)
fin = today

# ---------- ARCHIVOS POR DEFECTO ----------
img_file = open(icon_path, "rb")
font_zip = open(font_zip_path, "rb")

# ---------- PROCESAR FUENTES Y ARCHIVOS ----------
with zipfile.ZipFile(font_zip, 'r') as zip_ref:
    zip_ref.extractall("fuentes")

icon_hucha = Image.open(img_file).resize((150, 150)).convert("RGBA")

def cargar_fuente(nombre, size):
    path = os.path.join("fuentes", nombre)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()

title_font = cargar_fuente("Lato-Bold.ttf", 90)
label_font = cargar_fuente("Lato-Bold.ttf", 70)
value_font = cargar_fuente("Lato-Bold.ttf", 65)
small_font = cargar_fuente("Lato-Bold.ttf", 40)
tiny_font = cargar_fuente("Lato-Bold.ttf", 35)

# ---------- BANXICO ----------
@st.cache_data
def obtener_serie(clave, ini, fin):
    url = BASE_URL.format(clave, ini.strftime("%Y-%m-%d"), fin.strftime("%Y-%m-%d"))
    r = requests.get(url, headers=HEADERS)
    datos = r.json()["bmx"]["series"][0]["datos"]
    df = pd.DataFrame(datos)
    df["fecha"] = pd.to_datetime(df["fecha"], dayfirst=True)
    df["dato"] = pd.to_numeric(df["dato"].str.replace(",", ""), errors="coerce")
    return df.dropna().sort_values("fecha")

resumen_series = {}
series_largas = {}

for nombre, clave in SERIES.items():
    df = obtener_serie(clave, inicio, fin)
    if df is not None and len(df) >= 2:
        if nombre != "Tipo de Cambio FIX":
            resumen_series[nombre] = {
                "anterior": df["dato"].iloc[-2],
                "actual": df["dato"].iloc[-1]
            }
        series_largas[nombre] = df.set_index("fecha").resample("D").interpolate().reset_index()

# ---------- IMAGEN RESUMEN ----------
def generar_resumen_cetes():
    img = Image.new("RGB", (1080, 1350), "white")
    draw = ImageDraw.Draw(img)
    for y in range(1350):
        r = int(173 + (255 - 173) * y / 1350)
        g = int(216 + (255 - 216) * y / 1350)
        b = int(230 + (255 - 230) * y / 1350)
        draw.line([(0, y), (1080, y)], fill=(r, g, b))

    img.paste(icon_hucha, (900, 20), icon_hucha)
    draw.text((40, 40), "Resumen CETES", fill="#222222", font=title_font)

    y_pos = 180
    for plazo in ["28 Días", "91 Días", "182 Días", "364 Días", "728 Días"]:
        datos = resumen_series[plazo]
        draw.text((60, y_pos), plazo, fill="#D32F2F", font=label_font)
        draw.text((500, y_pos), f"Actual: {datos['actual']:.2f}%", fill="black", font=value_font)
        draw.text((500, y_pos + 70), f"Anterior: {datos['anterior']:.2f}%", fill="#555555", font=tiny_font)
        y_pos += 180

    tasa_obj = resumen_series.get("Tasa Objetivo", {"actual": 0, "anterior": 0})
    draw.multiline_text((60, y_pos + 10), "Tasa\nObjetivo", fill="#D32F2F", font=label_font, spacing=10)
    draw.text((500, y_pos + 10), f"Actual: {tasa_obj['actual']:.2f}%", fill="black", font=value_font)
    draw.text((500, y_pos + 80), f"Anterior: {tasa_obj['anterior']:.2f}%", fill="#555555", font=tiny_font)

    fecha_texto = fin.strftime("*datos para el %d de %B de %Y").replace("May", "Mayo")
    draw.text((40, 1270), fecha_texto, fill="#555555", font=small_font)
    draw.text((780, 1285), "Fuente: Banxico", fill="#555555", font=small_font)

    img.save("resumen_cetes.png")
    return img

generar_resumen_cetes()

# ---------- GRÁFICAS ----------
def generar_grafica_con_fondo():
    fig_width, fig_height, dpi = 1080, 1350, 100
    gradient_bg = Image.new("RGB", (fig_width, fig_height), "white")
    draw = ImageDraw.Draw(gradient_bg)
    for y in range(fig_height):
        r = int(173 + (255 - 173) * y / fig_height)
        g = int(216 + (255 - 216) * y / fig_height)
        b = int(230 + (255 - 230) * y / fig_height)
        draw.line([(0, y), (fig_width, y)], fill=(r, g, b))

    fig = plt.figure(figsize=(fig_width / dpi, fig_height / dpi))
    gs = GridSpec(len(series_largas) // 2 + 1, 2, figure=fig)
    fig.patch.set_alpha(0)
    fig.suptitle("CETES y Tipo de Cambio", fontsize=20)

    for i, (nombre, df) in enumerate(series_largas.items()):
        fechas = mdates.date2num(df["fecha"])
        valores = df["dato"].values
        row = i // 2
        col = i % 2
        ax = fig.add_subplot(gs[row, col])
        ax.plot(df["fecha"], valores, linewidth=2)
        ax.set_title(nombre)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=dpi, transparent=True)
    plt.close()
    buf.seek(0)

    fg = Image.open(buf).convert("RGBA").resize((fig_width, fig_height))
    bg = gradient_bg.convert("RGBA")
    final = Image.alpha_composite(bg, fg)
    final.save("graficas_cetes.png")
    return final

generar_grafica_con_fondo()

# ---------- MENSAJE FINAL ----------
st.success("✅ Imágenes generadas correctamente.")

st.markdown("""
### 📝 Resumen de archivos descargados

- **`resumen_cetes.png`**: Imagen con resumen de tasas CETES de 28 a 728 días y la tasa objetivo del Banxico, junto con su variación reciente.
- **`graficas_cetes.png`**: Gráfica que muestra la evolución de los CETES y el tipo de cambio FIX a lo largo del último año.
""")




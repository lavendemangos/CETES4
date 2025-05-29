# CETES4

# 📈 Streamlit CETES App

Esta aplicación de Streamlit genera visualizaciones automáticas con datos actualizados de los CETES (Certificados de la Tesorería) y el tipo de cambio FIX proporcionados por Banxico (Banco de México).

## 🚀 ¿Qué hace esta app?

- Descarga datos en tiempo real desde Banxico de tasas CETES a diferentes plazos (28 a 728 días) y tasa objetivo.
- Genera dos imágenes:
  - `resumen_cetes.png`: Resumen visual de tasas actuales y anteriores.
  - `graficas_cetes.png`: Gráfica histórica de tasas CETES y tipo de cambio FIX con fondo degradado.
- Utiliza fuentes y recursos gráficos incluidos localmente (no requiere carga manual de archivos).

## 📂 Estructura esperada

Asegúrate de tener la siguiente estructura:

```
📁 tu-proyecto/
├── app.py
├── requirements.txt
└── assets/
   
    └── lato.zip
```

> La carpeta `assets/` debe contener una imagen `hucha.png` y un archivo ZIP con la fuente `Lato-Bold.ttf`.

## ▶️ Cómo correr la app

1. Instala las dependencias:

```bash
pip install -r requirements.txt
```

2. Ejecuta la app:

```bash
streamlit run app.py
```

3. Revisa la carpeta: se generarán los archivos `resumen_cetes.png` y `graficas_cetes.png`.

## ✅ Requisitos

- Python 3.8 o superior
- Acceso a internet para consultar la API de Banxico

## 📦 Dependencias

Incluidas en `requirements.txt`:

- streamlit
- pandas
- numpy
- requests
- Pillow
- matplotlib

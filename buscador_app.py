import os
import re
import requests
import streamlit as st
from PIL import Image
from pdf2image import convert_from_path

# API OCR.Space
OCR_API_KEY = "helloworld"  # Puedes reemplazar con tu propia clave
OCR_API_URL = "https://api.ocr.space/parse/image"

def extraer_texto_ocr_space(imagen):
    buffered = imagen.convert("RGB")
    buffered.save("temp_img.png")
    with open("temp_img.png", "rb") as f:
        response = requests.post(
            OCR_API_URL,
            files={"file": f},
            data={"apikey": OCR_API_KEY, "language": "spa"}
        )
    os.remove("temp_img.png")
    resultado = response.json()
    try:
        return resultado["ParsedResults"][0]["ParsedText"]
    except:
        return ""

# Interfaz Streamlit
st.title("Buscador de palabras clave en archivos")

ruta_carpeta = st.text_input("📁 Ruta de la carpeta a analizar")
palabra_clave = st.text_input("🔍 Palabra clave a buscar")

if st.button("Buscar"):
    if not os.path.isdir(ruta_carpeta):
        st.error("La ruta ingresada no es válida.")
    elif not palabra_clave:
        st.warning("Por favor ingresa una palabra clave.")
    else:
        resultados = []

        for archivo in os.listdir(ruta_carpeta):
            ruta_archivo = os.path.join(ruta_carpeta, archivo)
            texto_extraido = ""

            # Archivos de texto
            if archivo.lower().endswith(".txt"):
                try:
                    with open(ruta_archivo, "r", encoding="utf-8") as f:
                        texto_extraido = f.read()
                except:
                    st.error(f"Error al leer {archivo}")

            # Imágenes
            elif archivo.lower().endswith((".jpg", ".jpeg", ".png")):
                try:
                    imagen = Image.open(ruta_archivo)
                    texto_extraido = extraer_texto_ocr_space(imagen)
                except:
                    st.error(f"Error al procesar imagen {archivo}")

            # PDFs escaneados
            elif archivo.lower().endswith(".pdf"):
                try:
                    paginas = convert_from_path(ruta_archivo)
                    for pagina in paginas:
                        texto_extraido += "\n" + extraer_texto_ocr_space(pagina)
                except:
                    st.error(f"Error al procesar PDF {archivo}")

            # Buscar palabra clave
            if re.search(palabra_clave, texto_extraido, re.IGNORECASE):
                resultados.append(archivo)

        # Mostrar resultados
        if resultados:
            st.success("Se encontró la palabra en los siguientes archivos:")
            for r in resultados:
                st.write(f"- {r}")
        else:
            st.info("No se encontró la palabra en ningún archivo.")

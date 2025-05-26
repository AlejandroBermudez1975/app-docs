import streamlit as st
import pandas as pd
import os
import re
from io import BytesIO
from PyPDF2 import PdfReader
import docx

# Función para extraer texto de archivos PDF
def extract_text_from_pdf(file):
    text = ""
    try:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    except:
        pass
    return text

# Función para extraer texto de archivos Word
def extract_text_from_word(file):
    text = ""
    try:
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except:
        pass
    return text

# Función para extraer emails
def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else ""

# Interfaz de la app
st.set_page_config(page_title="Extractor de Emails", layout="centered")

st.title("📄 Extraer Emails de Documentos")

uploaded_files = st.file_uploader("Sube hasta 100 archivos PDF o Word", type=["pdf", "docx"], accept_multiple_files=True)

if uploaded_files:
    progress_text = "⏳ Procesando archivos..."
    progress_bar = st.progress(0, text=progress_text)

    data = []

    for i, file in enumerate(uploaded_files):
        filename = file.name
        ext = os.path.splitext(filename)[1].lower()
        text = ""

        if ext == ".pdf":
            text = extract_text_from_pdf(file)
        elif ext == ".docx":
            text = extract_text_from_word(file)

        email = extract_email(text)

        data.append({
            "email": email,
            "archivo": filename
        })

        progress_bar.progress((i + 1) / len(uploaded_files), text=f"📁 Procesando: {filename}")

    # Crear Excel
    df = pd.DataFrame(data)
    df = df[["email", "archivo"]]  # Solo dejar estas dos columnas

    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    st.success("✅ ¡Extracción completada!")

    st.download_button(
        label="📥 Descargar Excel",
        data=output.getvalue(),
        file_name="resultados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

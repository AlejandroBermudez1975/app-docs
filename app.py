import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
from docx import Document
import re
from io import BytesIO

st.set_page_config(page_title="Extractor de Datos", layout="wide")

st.title("📄 Extraer Datos de Archivos PDF y Word")

uploaded_files = st.file_uploader("Sube hasta 100 archivos PDF o DOCX", type=["pdf", "docx"], accept_multiple_files=True)

progress_bar = st.progress(0)
status_text = st.empty()

data = []

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_info(text):
    name_match = re.search(r"(?i)(nombre|name)[:\s]+([A-ZÁÉÍÓÚÑa-záéíóúñ]+(\s[A-ZÁÉÍÓÚÑa-záéíóúñ]+)*)", text)
    email_match = re.search(r"[\w.-]+@[\w.-]+\.\w+", text)
    phone_match = re.search(r"\+?\d[\d\s().-]{7,}\d", text)

    name = name_match.group(2).strip() if name_match else ""
    email = email_match.group(0).strip() if email_match else ""
    phone = phone_match.group(0).strip() if phone_match else ""

    return name, email, phone

if uploaded_files:
    total_files = len(uploaded_files)
    for i, file in enumerate(uploaded_files):
        ext = os.path.splitext(file.name)[1].lower()
        text = ""
        if ext == ".pdf":
            text = extract_text_from_pdf(file)
        elif ext == ".docx":
            text = extract_text_from_docx(file)

        name, email, phone = extract_info(text)
        data.append([name, email, phone, file.name])

        progress_bar.progress((i + 1) / total_files)
        status_text.text(f"Procesando: {file.name}")

    status_text.text("✅ ¡Listo! Descarga los datos abajo.")
    df = pd.DataFrame(data, columns=["Nombre", "Email", "Teléfono", "Archivo"])

    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    st.download_button(
        label="📥 Descargar Excel",
        data=output.getvalue(),
        file_name="datos_extraidos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

import fitz  # PyMuPDF
from docx import Document
import re
import pandas as pd
import streamlit as st
import os
import io

def extract_text_from_pdf(pdf_path):
    text = ""
    pdf_document = fitz.open(pdf_path)
    for page in pdf_document:
        text += page.get_text().strip() + "\n"
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text.strip() + "\n"
    return text

def extract_data_from_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_extension.lower() in ['.docx', '.doc']:
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Please upload a PDF or Word document.")

    # Extract OS number
    ordre_de_service = re.search(r'\d{4}[A-Z]+\d{3}_OS_\d{4}', text)
    OS_number = ordre_de_service.group() if ordre_de_service else "Not found"

    # Extract PNP ID
    pnp_id_matches = re.findall(r'PNP \d+ \d+\s:', text)
    PNPs = [match.strip(" :") for match in pnp_id_matches] if pnp_id_matches else []

    # Extract libellé
    libelle_matches = re.findall(r'Libellé de la prestation :(.+?)\.', text, re.DOTALL)
    libelles = [match.strip() for match in libelle_matches] if libelle_matches else []

    # Extract description
    description_matches = re.findall(r'Description de la prestation :(.+?)\.', text, re.DOTALL)
    descriptions = [match.strip() for match in description_matches] if description_matches else []

    # Extract price
    prix_matches = re.findall(r'Prix forfaitaire :(.+?)\.', text, re.DOTALL)
    prices = [match.strip() for match in prix_matches] if prix_matches else []

    # Extract conditions de paiement
    conditions_paiement_matches = re.findall(r'Conditions de paiement :(.+?)\.', text, re.DOTALL)
    c_paiement = [match.strip() for match in conditions_paiement_matches] if conditions_paiement_matches else []

    # Create a DataFrame
    max_length = max(len(PNPs), len(libelles), len(descriptions), len(prices), len(c_paiement))
    data = {
        'PNP_ID': PNPs + [None] * (max_length - len(PNPs)),
        'Libellé': libelles + [None] * (max_length - len(libelles)),
        'Description': descriptions + [None] * (max_length - len(descriptions)),
        'Prix_forfaitaire': prices + [None] * (max_length - len(prices)),
        'OS': [OS_number] * max_length,
        'Echeancier': c_paiement + [None] * (max_length - len(c_paiement))
    }
    return pd.DataFrame(data)

st.title('Multi-File PDF and Word Data Extractor')

uploaded_files = st.file_uploader("Choose PDF or Word files", type=["pdf", "docx", "doc"], accept_multiple_files=True)

if uploaded_files:
    st.write(f"{len(uploaded_files)} file(s) uploaded successfully.")

    if st.button("Generate Excel"):
        try:
            all_data = []
            for uploaded_file in uploaded_files:
                # Save the uploaded file temporarily
                file_path = f"temp_{uploaded_file.name}"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Extract data from the uploaded file
                df = extract_data_from_file(file_path)
                all_data.append(df)

                # Clean up the temporary file
                os.remove(file_path)

            # Combine all dataframes
            combined_df = pd.concat(all_data, ignore_index=True)
            st.write(combined_df)
            # Generate Excel file
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                combined_df.to_excel(writer, index=False, sheet_name='Extracted Data')

            st.download_button(
                label="Download Excel file",
                data=excel_buffer.getvalue(),
                file_name="extracted_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.success("Excel file generated successfully!")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
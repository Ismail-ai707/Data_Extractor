import fitz  # PyMuPDF
import re
import pandas as pd
import streamlit as st

def extract_data_from_pdf(pdf_path):
    text = ""
    # Open the PDF document
    pdf_document = fitz.open(pdf_path)
    # Iterate through pages and extract text
    for page in pdf_document:
        pageContent = page.get_text()
        text += pageContent.strip() + "\n"
    
    # Extract OS number
    ordre_de_service = re.search(r'\d{4}[A-Z]+\d{3}_OS_\d{4}', text)
    OS_number = ordre_de_service.group() if ordre_de_service else "Not found"
    st.write("Ordre de Service N°:", OS_number)

    # Extract PNP ID
    pnp_id_matches = re.findall(r'PNP \d+ \d+ :', text)
    PNPs = [match.strip(" :") for match in pnp_id_matches] if pnp_id_matches else []
    st.write("PNP IDs:", PNPs)

    # Extract libellé
    libelle_matches = re.findall(r'Libellé de la prestation :(.+?)\.', text, re.DOTALL)
    libelles = [match.strip() for match in libelle_matches] if libelle_matches else []
    st.write("Libellés:", libelles)

    # Extract description
    description_matches = re.findall(r'Description de la prestation :(.+?)\.', text, re.DOTALL)
    descriptions = [match.strip() for match in description_matches] if description_matches else []
    st.write("Descriptions:", descriptions)

    # Extract price
    prix_matches = re.findall(r'Prix forfaitaire :(.+?)\.', text, re.DOTALL)
    prices = [match.strip() for match in prix_matches] if prix_matches else []
    st.write("Prix:", prices)

    # Extract conditions de paiement
    conditions_paiement_matches = re.findall(r'Conditions de paiement :(.+?)\.', text, re.DOTALL)
    c_paiement = [match.strip() for match in conditions_paiement_matches] if conditions_paiement_matches else []
    st.write("Echeancier:", c_paiement)

    st.write("Lengths: ", len(PNPs), len(libelles), len(descriptions), len(prices), len(c_paiement))

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
    df = pd.DataFrame(data)
    st.write(df)
    return df

st.title('PDF Data Extractor')
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save the uploaded file temporarily
    with open("uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.write("File uploaded successfully.")

    try:
        # Extract data from the uploaded PDF
        extracted_df = extract_data_from_pdf("uploaded_file.pdf")

        # Provide an option to download the extracted data as CSV
        csv_filename = "extracted_data.csv"
        extracted_df.to_csv(csv_filename, index=False)
        with open(csv_filename, "r") as file:
            csv_contents = file.read()
        
        st.download_button(
            label="Download data as CSV",
            data=csv_contents,
            file_name=csv_filename,
            mime='text/csv',
        )
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
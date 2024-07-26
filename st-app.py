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
        pageContent.strip()
        text += pageContent
    
    # Extract OS number
    ordre_de_service = re.search(r'\d{4}[A-Z]+\d{3}_OS_\d{4}', text)
    
    # Check if a match is found for number of OS
    if ordre_de_service:
        OS_number = ordre_de_service.group()
        st.write("Ordre de Service N°:", OS_number)
    
    # Extract PNP ID
    pnp_id_matches = re.findall(r'PNP \d+ \d+', text)
    pnp_ids = pnp_id_matches if pnp_id_matches else None
    pnps_stripped = [pnp_ids[i].strip(" :") for i in range(len(pnp_ids))]
    PNPs = pnps_stripped
    st.write("PNP IDs:", PNPs)
    
    # Extract libellé
    libelle_matches = re.findall(r'Libellé de la prestation :(.+?)\.', text, re.DOTALL)
    libelles = [match.strip() for match in libelle_matches] if libelle_matches else None
    st.write("Libellés:", libelles)

    # Extract description
    description_matches = re.findall(r'Description de la prestation :(.+?)\.', text, re.DOTALL)
    descriptions = [match.strip() for match in description_matches] if description_matches else None
    st.write("Descriptions:", descriptions)
    
    # Extract price
    prix_matches = re.findall(r'Prix forfaitaire :(.+?)\.', text, re.DOTALL)
    prices = [match.strip() for match in prix_matches] if prix_matches else None
    st.write("Prix:", prices)

    # Extract conditions de paiement
    conditions_paiement_matches = re.findall(r'Conditions de paiement :(.+?)\.', text, re.DOTALL)
    c_paiement = [match.strip() for match in conditions_paiement_matches] if conditions_paiement_matches else None
    st.write("Echeancier:", c_paiement)

    st.write("Lengths: ", len(pnps_stripped), len(libelles), len(descriptions), len(prices), len(c_paiement))
    
    # Create a DataFrame
    data = {
        'PNP_ID': PNPs,
        'Libellé': libelles,
        'Description': descriptions,
        'Prix_forfaitaire': prices,
        'OS': OS_number,
        'Echeancier': c_paiement
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
    
    # Extract data from the uploaded PDF
    extracted_df = extract_data_from_pdf("uploaded_file.pdf")
    
    # Provide an option to download the extracted data as CSV
    csv_filename = "extracted_data.csv"
    extracted_df.to_csv(csv_filename, index=False)
    
    st.download_button(
        label="Download data as CSV",
        data=open(csv_filename).read(),
        file_name=csv_filename,
        mime='text/csv',
    )



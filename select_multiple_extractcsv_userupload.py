import google.generativeai as genai
import PyPDF2
import streamlit as st
import csv
from io import StringIO, BytesIO

# Access the API key
api_key = st.secrets["API_KEY"]
genai.configure(api_key=api_key)


# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


# Function to extract information based on query
def extract_information(query, text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Given the following text from a research paper, extract information relevant to this query: '{query}'. Return only the extracted information, nothing else.\n\nText: {text}"
    response = model.generate_content(prompt)
    return response.text


# Function to convert results to CSV
def results_to_csv(results):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Article Name', 'Extracted Information'])
    for article, info in results.items():
        writer.writerow([article, info])
    return output.getvalue()


# Streamlit Interface
st.title("PDF Information Extractor")

# File uploader
uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

# Query input
query = st.text_input("Enter your query for information extraction:")

if st.button("Extract Information") and uploaded_files and query:
    results = {}
    for uploaded_file in uploaded_files:
        # Extract text from the uploaded PDF
        pdf_text = extract_text_from_pdf(BytesIO(uploaded_file.read()))

        # Extract information based on the query
        extracted_info = extract_information(query, pdf_text)

        # Store the results
        results[uploaded_file.name] = extracted_info

    if results:
        # Convert results to CSV
        csv_results = results_to_csv(results)

        # Display results
        st.text_area("Extracted Information (CSV format)", csv_results, height=300)

        # Option to download CSV
        st.download_button(
            label="Download CSV",
            data=csv_results,
            file_name="extracted_information.csv",
            mime="text/csv"
        )
    else:
        st.warning("No information could be extracted. Please check your query and try again.")
else:
    st.info("Please upload PDF files and enter a query, then click 'Extract Information'.")
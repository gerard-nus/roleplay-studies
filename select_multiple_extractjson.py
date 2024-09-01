import google.generativeai as genai
import PyPDF2
import streamlit as st
import os
import csv
from io import StringIO

# Access the API key
api_key = st.secrets["API_KEY"]
genai.configure(api_key=api_key)


# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text


# Preloading PDFs
pdf_directory = "./pdfs"
pdf_files = [os.path.join(pdf_directory, file) for file in os.listdir(pdf_directory) if file.endswith('.pdf')]

syllabus_texts = {}
for pdf_file in pdf_files:
    syllabus_texts[os.path.basename(pdf_file)] = extract_text_from_pdf(pdf_file)


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

# Query input
query = st.text_input("Enter your query for information extraction:")

# Multiple syllabus selection
selected_syllabi = st.multiselect("Select studies to query", list(syllabus_texts.keys()),
                                  default=list(syllabus_texts.keys())[0])

if st.button("Extract Information"):
    if query and selected_syllabi:
        results = {}
        for syllabus in selected_syllabi:
            extracted_info = extract_information(query, syllabus_texts[syllabus])
            results[syllabus] = extracted_info

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
        st.warning("Please enter a query and select at least one study.")
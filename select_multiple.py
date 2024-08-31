import google.generativeai as genai
import PyPDF2
import streamlit as st
import os

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

# Response Generation Function
def generate_response(messages, selected_syllabi_texts):
    model = genai.GenerativeModel('gemini-1.5-flash')
    conversation_history = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    combined_syllabus_text = "\n\n".join(selected_syllabi_texts)
    prompt = f"Syllabus information:\n{combined_syllabus_text}\n\nConversation history:\n{conversation_history}\nAI:"
    response = model.generate_content(prompt)
    return response.text

# Streamlit Interface
st.title("Multi-document Social Work Studies Chatbot")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Multiple syllabus selection
selected_syllabi = st.multiselect("Select studies to query", list(syllabus_texts.keys()), default=list(syllabus_texts.keys())[0])

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask a question about the selected studies"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    selected_syllabi_texts = [syllabus_texts[syllabus] for syllabus in selected_syllabi]
    with st.chat_message("assistant"):
        response = generate_response(st.session_state.messages, selected_syllabi_texts)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
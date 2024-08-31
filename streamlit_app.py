import google.generativeai as genai
import PyPDF2
import streamlit as st
import os


# Access the API key
api_key = st.secrets["API_KEY"]
    # this is stored in streamlit dashboard -> see the streamlit website


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

# Response Generation Function:
# Response Generation Function
def generate_response(messages, syllabus_text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    conversation_history = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    prompt = f"Syllabus information: {syllabus_text}\n\nConversation history:\n{conversation_history}\nAI:"
    response = model.generate_content(prompt)
    return response.text


# Streamlit Interface
st.title("SW4103 Syllabus, Notes, Assignment Guidelines  Chatbot")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Syllabus selection
selected_syllabus = st.selectbox("Select a syllabus to query", list(syllabus_texts.keys()))

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask a question about the selected document"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    syllabus_text = syllabus_texts[selected_syllabus]
    with st.chat_message("assistant"):
        response = generate_response(st.session_state.messages, syllabus_text)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
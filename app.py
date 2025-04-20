import streamlit as st
import google.generativeai as genai
import os
import base64
import uuid
from PyPDF2 import PdfReader

# Configure API
genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-pro")

# System prompt
system_prompt = {
     "role": "user",
    "parts": """
You are a Compliance and Law Assistant expert designed to support legal professionals, compliance officers, and corporate teams. Your responsibilities include:
- Interpreting and summarizing laws, regulations, and compliance requirements (e.g., GDPR, HIPAA, SOX, PCI DSS).
- Drafting legal and compliance documents like privacy policies, terms, contracts.
- Identifying legal risks and suggesting mitigation strategies.
- Supporting regulatory reporting, compliance tracking, and due diligence.
- Answering legal questions accurately and clearly.

When answering:
- Use clear, professional language.
- Provide disclaimers that your response is not legal advice.
- Cite laws or regulations when applicable.
- Ask for clarification if the query lacks context.

Begin by introducing yourself and asking how you can assist with legal or compliance needs today.
"""
}

# Get unique user ID
if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())

# Init session messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [system_prompt]

# UI
st.title("📚 Compliance & Legal Assistant Chatbot")
st.markdown("💼 I can help with regulations, drafting documents, summaries, and more.")

# PDF Upload
uploaded_file = st.file_uploader("📄 Upload a PDF (e.g., contract, policy, legal doc)", type=["pdf"])
if uploaded_file:
    reader = PdfReader(uploaded_file)
    pdf_text = "\n\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    st.session_state["messages"].append({"role": "user", "parts": f"Extracted from uploaded PDF:\n{pdf_text[:3000]}"})  # Truncate if long

# Chat Input
user_input = st.text_input("💬 How can I assist you today?", key="chat_input")

# Chat Response
if user_input:
    st.session_state["messages"].append({"role": "user", "parts": user_input})
    try:
        response = model.generate_content(st.session_state["messages"])
        st.session_state["messages"].append({"role": "model", "parts": response.text})
        # Log to file
        with open(f"logs/{st.session_state['user_id']}.txt", "a") as f:
            f.write(f"\nUser: {user_input}\nBot: {response.text}\n")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Display messages
for msg in st.session_state["messages"][1:]:
    role = "🧑" if msg["role"] == "user" else "🤖"
    st.markdown(f"**{role}:** {msg['parts']}")


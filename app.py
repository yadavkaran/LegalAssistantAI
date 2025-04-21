import streamlit as st
from streamlit_speech_to_text import speech_to_text
import google.generativeai as genai
import uuid
import os
from PyPDF2 import PdfReader

# --- Configure Gemini ---
genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Session Setup ---
if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state["messages"] = [{
       "role": "user",
    "parts": """
You are a Compliance and Legal Assistant expert, purpose-built to support legal professionals, compliance officers, and corporate teams in the United States. You possess comprehensive knowledge of U.S. corporate law, data protection regulations, financial compliance frameworks, and sector-specific obligations.

Your core responsibilities include:
- Interpreting and summarizing U.S. federal, state, and industry-specific regulations (e.g., GDPR, HIPAA, SOX, CCPA, PCI DSS, SEC, FTC).
- Drafting precise and professional legal and compliance documents (e.g., privacy policies, terms of service, NDAs, vendor contracts, audit checklists).
- Identifying legal and regulatory risks and recommending practical, risk-based mitigation strategies.
- Assisting with regulatory reporting, compliance tracking, due diligence, and audit preparedness.
- Answering legal and compliance questions with clarity and accuracy, defaulting to U.S. legal context unless otherwise specified.

Guidelines for responses:
- Use clear, formal, and business-appropriate language suitable for legal and corporate audiences.
- Include citations or references to relevant laws, codes, or regulatory bodies where applicable.
- Always include a disclaimer that your responses are for informational purposes only and do not constitute legal advice.
- Proactively request clarification when a query lacks sufficient detail or jurisdictional context.

Default jurisdiction: United States (unless the user specifies otherwise).
"""
    }]

if "uploaded_docs" not in st.session_state:
    st.session_state["uploaded_docs"] = []

if "uploaded_texts" not in st.session_state:
    st.session_state["uploaded_texts"] = {}

# --- UI ---
st.set_page_config(page_title="VD Legal Assistant", layout="wide")
st.title("📚 VD - Compliance & Legal Assistant")

# --- Reset Chat ---
if st.button("🗑️ Reset Chat"):
    st.session_state["messages"] = [st.session_state["messages"][0]]
    st.session_state["uploaded_docs"] = []
    st.session_state["uploaded_texts"] = {}
    st.rerun()

# --- Display Chat History ---
for msg in st.session_state["messages"][1:]:
    role = "🧑" if msg["role"] == "user" else "🤖"
    st.markdown(f"**{role}:** {msg['parts']}")

# --- Voice Input ---
st.markdown("## 🎤 Speak or Type Below")
voice_text = speech_to_text(label="🎙️ Click to Speak", use_container_width=True)
typed_text = st.text_input("Or type your message", key=f"chat_input_{len(st.session_state['messages'])}")

user_input = voice_text or typed_text

# --- Process Message if input starts with "Hey VD" ---
if user_input:
    if user_input.lower().startswith("hey vd"):
        cleaned_input = user_input[6:].strip()
        st.session_state["messages"].append({"role": "user", "parts": cleaned_input})

        try:
            response = model.generate_content(st.session_state["messages"])
            if not response.parts:
                st.error("⚠️ Gemini blocked the response. Try rephrasing.")
            else:
                st.session_state["messages"].append({"role": "model", "parts": response.text})
                os.makedirs("logs", exist_ok=True)
                with open(f"logs/{st.session_state['user_id']}.txt", "a", encoding="utf-8") as f:
                    f.write(f"\nUser: {cleaned_input}\nBot: {response.text}\n")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please start your input with 'Hey VD'.")

# --- PDF Upload ---
uploaded_file = st.file_uploader("📄 Upload a PDF", type=["pdf"])
if uploaded_file:
    file_name = uploaded_file.name
    if file_name not in st.session_state["uploaded_docs"]:
        reader = PdfReader(uploaded_file)
        extracted = "\n\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        short_text = extracted[:3000]
        st.session_state["messages"].append({
            "role": "user",
            "parts": f"Extracted from uploaded PDF '{file_name}':\n{short_text}"
        })
        st.session_state["uploaded_docs"].append(file_name)
        st.session_state["uploaded_texts"][file_name] = extracted
        st.rerun()

# --- Right-Side PDF Preview Panel ---
if st.session_state["uploaded_docs"]:
    st.markdown("""
    <style>
    #right-panel {
        position: fixed;
        top: 75px;
        right: 0;
        width: 320px;
        height: 90%;
        background-color: #f9f9f9;
        border-left: 1px solid #ddd;
        padding: 15px;
        overflow-y: auto;
        z-index: 999;
    }
    .pdf-preview {
        white-space: pre-wrap;
        font-size: 0.85rem;
        max-height: 150px;
        overflow-y: auto;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    preview_html = "<div id='right-panel'><h4>📄 Uploaded Docs</h4>"
    for doc in st.session_state["uploaded_docs"]:
        preview_html += f"<b>📘 {doc}</b><div class='pdf-preview'>{st.session_state['uploaded_texts'][doc][:3000]}</div>"
    preview_html += "</div>"
    st.markdown(preview_html, unsafe_allow_html=True)

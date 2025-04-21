import streamlit as st
from streamlit_speech_to_text import speech_to_text
import google.generativeai as genai
import uuid
import os
from PyPDF2 import PdfReader

# --- Configure Gemini ---
genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Session State ---
if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state["messages"] = [{
        "role": "user",
        "parts": """
You are a Compliance and Legal Assistant expert, purpose-built to support legal professionals, compliance officers, and corporate teams in the United States.
You help explain regulations (GDPR, HIPAA, SOX, PCI DSS), draft legal docs (NDAs, policies), and analyze uploaded content.
Always include a disclaimer: “This is not legal advice.”
"""
    }]

if "uploaded_docs" not in st.session_state:
    st.session_state["uploaded_docs"] = []

if "uploaded_texts" not in st.session_state:
    st.session_state["uploaded_texts"] = {}

# --- Page Config ---
st.set_page_config(page_title="VD Legal Assistant", layout="wide")
st.title("📚 VD - Compliance & Legal Assistant")

# --- Reset Chat ---
if st.button("🗑️ Reset Chat"):
    st.session_state["messages"] = [st.session_state["messages"][0]]
    st.session_state["uploaded_docs"] = []
    st.session_state["uploaded_texts"] = {}
    st.rerun()

# --- Display Chat ---
for msg in st.session_state["messages"][1:]:
    role = "🧑" if msg["role"] == "user" else "🤖"
    st.markdown(f"**{role}:** {msg['parts']}")

# --- Voice + Text Input ---
st.markdown("## 🎤 Speak or Type Your Message")
voice_text = speech_to_text(label="🎙️ Speak", use_container_width=True)
typed_text = st.text_input("Or type here", key=f"chat_input_{len(st.session_state['messages'])}")

user_input = voice_text or typed_text

# --- Process Input ---
if user_input:
    st.session_state["messages"].append({"role": "user", "parts": user_input})

    try:
        response = model.generate_content(st.session_state["messages"])
        if not response.parts:
            st.error("⚠️ Gemini blocked the response. Try rephrasing.")
        else:
            st.session_state["messages"].append({"role": "model", "parts": response.text})
            os.makedirs("logs", exist_ok=True)
            with open(f"logs/{st.session_state['user_id']}.txt", "a", encoding="utf-8") as f:
                f.write(f"\nUser: {user_input}\nBot: {response.text}\n")
        st.rerun()
    except Exception as e:
        st.error(f"Error: {str(e)}")

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

# --- Floating Preview Panel ---
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

import streamlit as st
import google.generativeai as genai
import os
import uuid
from PyPDF2 import PdfReader
from PIL import Image
import random

# --- Page setup ---
st.set_page_config(page_title="VD Legal Assistant", layout="wide")

# --- Theme Toggle ---
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

toggle = st.toggle("🌙 Dark Mode" if st.session_state["theme"] == "light" else "☀️ Light Mode", value=(st.session_state["theme"] == "dark"))
st.session_state["theme"] = "dark" if toggle else "light"

if st.session_state["theme"] == "dark":
    st.markdown("""
        <style>
            body, .stApp { background-color: #121212; color: #e0e0e0; }
            .css-18e3th9 { background-color: #1e1e1e; }
            .css-1d391kg { color: white; }
        </style>
    """, unsafe_allow_html=True)


# --- State setup ---
if "page" not in st.session_state:
    st.session_state.page = "home"

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

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

# --- Gemini setup ---
genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Page 1: Landing View ---
def home():
    horizontal_bar = "<hr style='margin-top: 0; margin-bottom: 0; height: 1px; border: 1px solid #635985;'><br>"

    with st.sidebar:
        st.subheader("🧠 VD - Legal Assistant")
        st.markdown(horizontal_bar, True)
        sidebar_logo = Image.open("VD.jpg").resize((300, 390))
        st.image(sidebar_logo, use_container_width='auto')

        st.markdown("""
        **What can VD do?**
        - 🧾 Summarize regulations (SOX, HIPAA, CCPA)
        - 📝 Draft NDAs, policies, checklists
        - 📁 Analyze uploaded PDFs

        _Disclaimer: AI-generated responses are informational only._
        """, unsafe_allow_html=True)

    # Help Content with PixMatch-style layout
    hlp_dtl = f"""<span style="font-size: 24px;">
    <ol>
    <li style="font-size:15px;">VD helps you interpret U.S. corporate, privacy, and compliance laws.</li>
    <li style="font-size:15px;">You can upload a PDF (e.g., contract, NDA, policy) and VD will summarize or extract key content.</li>
    <li style="font-size:15px;">Ask questions like: “What does SOX require for financial reporting?”</li>
    <li style="font-size:15px;">All queries and uploads are session-based and not stored permanently.</li>
    <li style="font-size:15px;">This tool is for informational use and does not replace legal counsel.</li>
    </ol></span>"""

    st.title("📚 Welcome to VD - Compliance & Legal Assistant")
    st.markdown(horizontal_bar, True)

    col1, col2 = st.columns(2)

    with col2:
        law_image = Image.open(random.choice(["vd1.jpg", "vd2.jpg", "vd3.jpg"])).resize((550, 550))
        st.image(law_image, use_container_width='auto')

    with col1:
        st.subheader("📌 How It Works")
        st.markdown(horizontal_bar, True)
        st.markdown(hlp_dtl, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)


    st.markdown(horizontal_bar, True)
    st.markdown("🔒 This AI assistant does not give legal advice.", unsafe_allow_html=True)
    st.markdown("<strong>Built by: 😎 KARAN YADAV, RUSHABH MAKWANA, ANISH AYARE</strong>", unsafe_allow_html=True)

    if st.button("💬 Ask VD"):
        st.session_state.page = "chat"
        st.rerun()

# --- Page 2: Chatbot View ---
def show_chat():
    st.title("📚 VD - Legal Chat Assistant")

    if st.button("🔙 Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    if st.button("🗑️ Reset Chat"):
        st.session_state["messages"] = [st.session_state["messages"][0]]
        st.session_state["uploaded_docs"] = []
        st.session_state["uploaded_texts"] = {}
        st.rerun()

    # Chat history
    for msg in st.session_state["messages"][1:]:
        role = "🧑" if msg["role"] == "user" else "🤖"
        st.markdown(f"**{role}:** {msg['parts']}")

    # Input field
    user_input = st.text_input("💬 How can I assist you today?", key=f"chat_input_{len(st.session_state['messages'])}")
    if user_input:
        st.session_state["messages"].append({"role": "user", "parts": user_input})
        try:
            response = model.generate_content(st.session_state["messages"])
            st.session_state["messages"].append({"role": "model", "parts": response.text})

            os.makedirs("logs", exist_ok=True)
            with open(f"logs/{st.session_state['user_id']}.txt", "a", encoding="utf-8") as f:
                f.write(f"\nUser: {user_input}\nBot: {response.text}\n")

            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # PDF upload
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

    # Preview Panel
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

# --- Run the page ---
if st.session_state.page == "home":
    home()
else:
    show_chat()

import streamlit as st
import google.generativeai as genai
import os
import uuid
from PyPDF2 import PdfReader

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

# --- Page setup ---
st.set_page_config(page_title="VD Legal Assistant", layout="wide")

# --- State setup ---
if "page" not in st.session_state:
    st.session_state.page = "home"

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

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

# --- Gemini setup ---
genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Page 1: Landing View ---
def show_home():
    st.title("🤖 Welcome to VD - Compliance & Legal Assistant")
    st.markdown("""
    <style>
    .vd-banner {
        font-size: 20px;
        padding: 20px;
        border: 1px solid #ccc;
        border-radius: 10px;
        background-color: rgba(240,240,240,0.7);
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="vd-banner">
        <strong>VD</strong> is your virtual legal compliance assistant.  
        It helps with:
        - 🧾 Regulatory summaries (e.g. SOX, HIPAA, CCPA)
        - 📄 Document analysis (PDFs)
        - ✍️ Drafting legal policies and checklists
        - ❓ Answering legal/compliance questions (U.S.-focused)

        <br><br>
        <i>Disclaimer: This app provides informational guidance only and does not constitute legal advice.</i>
    </div>
    """, unsafe_allow_html=True)

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
    show_home()
else:
    show_chat()

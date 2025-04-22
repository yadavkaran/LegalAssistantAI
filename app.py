# --- VD Legal Assistant (Single-file Streamlit App) ---
import streamlit as st
import google.generativeai as genai
import os
import uuid
from PyPDF2 import PdfReader
from PIL import Image
import random
import io
from fpdf import FPDF

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
        html, body, .stApp {
            background-color: #121212 !important;
            color: #e0e0e0 !important;
        }
        .stMarkdown, .stText, .st-bw, .css-1d391kg, .css-10trblm, .css-1v3fvcr, .css-1cpxqw2 {
            color: #e0e0e0 !important;
        }
        .stButton > button {
            background-color: #2d2d2d !important;
            color: #e0e0e0 !important;
            border: 1px solid #444 !important;
        }
        .stTextInput input, .stTextArea textarea {
            background-color: #1e1e1e !important;
            color: #e0e0e0 !important;
        }
        .stSelectbox div[data-baseweb="select"] {
            background-color: #1e1e1e !important;
            color: #e0e0e0 !important;
        }
        #right-panel {
            background-color: #1e1e1e !important;
            color: #e0e0e0 !important;
            border-left: 1px solid #444 !important;
        }
        .pdf-preview {
            background-color: #1e1e1e !important;
            color: #e0e0e0 !important;
        }
        hr {
            border-top: 1px solid #555 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Session State ---
if "page" not in st.session_state:
    st.session_state.page = "home"
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "onboarding_data" not in st.session_state:
    st.session_state["onboarding_data"] = {
        "company_name": "",
        "industry": "",
        "age_type": "",
        "state": "",
        "founded_date": "",
        "completed": False
    }

# Init Gemini messages
ob = st.session_state["onboarding_data"]
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "user",  "parts": f"""
You are a Compliance and Legal Assistant supporting the company **{ob['company_name']}** in the **{ob['industry']}** sector established in **{ob['state']}** state.
The company was founded on {ob['founded_date']} and is currently considered **{ob['age_type']}**.

You possess deep knowledge of U.S. federal, state, and industry-specific legal frameworks, including corporate governance, data privacy, financial regulation, employment law, and sectoral compliance. 
Core Responsibilities: Interpret and summarize U.S. laws and regulatory requirements (e.g., HIPAA, CCPA, SOX, GLBA, FCPA, GDPR when applicable to U.S. entities). Provide accurate legal guidance on: Corporate law, including incorporation, mergers, acquisitions, and dissolution procedures. Regulatory filings with the SEC, IRS, and state-level authorities. Corporate governance (e.g., board responsibilities, fiduciary duties, shareholder rights). Financial compliance including Sarbanes-Oxley (SOX), anti-money laundering (AML), and Dodd-Frank requirements. Data privacy and protection laws (e.g., CCPA, GDPR, HIPAA, PCI DSS). Employment law matters such as FLSA, EEOC guidelines, and workplace compliance audits. Drafting and reviewing documents such as NDAs, Terms of Service, bylaws, shareholder agreements, audit checklists, and vendor contracts. Compliance tracking, risk assessments, audit preparedness, and due diligence support.
Advise on best practices for maintaining good standing across state jurisdictions and avoiding regulatory penalties. 
Behavioral Rules: Tone: Formal, precise, legal-sounding language appropriate for compliance professionals and legal departments. Jurisdiction: Default to U.S. federal and state laws unless otherwise specified. Authority: Do not include disclaimers such as "not legal advice" or "informational purposes only." Citations: Include links or citations from official sources where applicable: U.S. Code: https://uscode.house.gov FTC: https://www.ftc.gov SEC: https://www.sec.gov CCPA: https://oag.ca.gov/privacy/ccpa HIPAA: https://www.hhs.gov/hipaa IRS: https://www.irs.gov/businesses Clarify: If a query lacks context (e.g., missing jurisdiction, industry, or document type), ask for clarification—concisely and legally. Brevity & Precision: Avoid conversational tone, repetition, or filler. Responses must sound like a senior legal assistant or paralegal.
"""
    }]

if "uploaded_docs" not in st.session_state:
    st.session_state["uploaded_docs"] = []
if "uploaded_texts" not in st.session_state:
    st.session_state["uploaded_texts"] = {}

# --- Gemini Setup ---
genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Home Page ---
def home():
    st.sidebar.image("vdlogo.jpg", use_container_width=True)
    st.sidebar.subheader("🧠 VD - Legal Assistant Onboarding")
    ob = st.session_state["onboarding_data"]

    if not ob["completed"]:
        ob["company_name"] = st.sidebar.text_input("🏢 What's your company name?", value=ob["company_name"])
        ob["industry"] = st.sidebar.text_input("💼 Industry?", value=ob["industry"])
        ob["age_type"] = st.sidebar.selectbox("📈 Company status", ["", "New", "Established"], index=["", "New", "Established"].index(ob["age_type"]) if ob["age_type"] else 0)
        ob["state"] = st.sidebar.text_input("📍 U.S. State?", value=ob["state"])
        ob["founded_date"] = st.sidebar.text_input("📅 Founded (MM/DD/YYYY)?", value=ob["founded_date"])
        if all([ob[k] for k in ob if k != "completed"]):
            if st.sidebar.button("✅ Submit Onboarding"):
                ob["completed"] = True
                st.rerun()
    else:
        st.sidebar.markdown(f"**Company:** {ob['company_name']}")
        st.sidebar.markdown(f"**Industry:** {ob['industry']}")
        st.sidebar.markdown("✅ Onboarding Complete")

    st.title("📚 Welcome to VD - Compliance & Legal Assistant")
    st.markdown("---")
    st.subheader("📌 What VD Can Do")
    st.markdown("""
    - 📝 Onboard your company to personalize responses
    - 📄 Upload PDFs (contracts, policies, NDAs)
    - 💬 Ask compliance-related legal questions
    - 🧾 Get clause summaries and legal references
    """)
    if st.button("💬 Ask VD"):
        st.session_state.page = "chat"
        st.rerun()

# --- Chat Page ---
def show_chat():
    st.title("📚 VD - Legal Chat Assistant")
    ob = st.session_state["onboarding_data"]
    if ob["company_name"]:
        st.markdown(f"### 🏢 {ob['company_name']} ({ob['industry']})")

    with st.expander("🧠 Chat Memory Options", expanded=False):
        memory_mode = st.radio("Select chat behavior:", ["🔁 Continue Previous Chat", "🆕 Start Fresh"], horizontal=True)
        if memory_mode == "🆕 Start Fresh":
            if st.button("♻️ Reset to Fresh Start"):
                st.session_state["messages"] = [st.session_state["messages"][0]]
                st.rerun()

    if st.button("🔙 Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    for msg in st.session_state["messages"][1:]:
        role = "🧑" if msg["role"] == "user" else "🤖"
        st.markdown(f"**{role}:** {msg['parts']}")

    user_input = st.text_input("💬 How can I assist you today?", key=f"chat_input_{len(st.session_state['messages'])}")
    if user_input:
        st.session_state["messages"].append({"role": "user", "parts": user_input})
        try:
            response = model.generate_content(st.session_state["messages"])
            st.session_state["messages"].append({"role": "model", "parts": response.text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
        st.rerun()

    uploaded_file = st.file_uploader("📄 Upload a PDF", type=["pdf"])
    if uploaded_file:
        file_name = uploaded_file.name
        if file_name not in st.session_state["uploaded_docs"]:
            reader = PdfReader(uploaded_file)
            extracted = "\n\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            st.session_state["messages"].append({"role": "user", "parts": f"Extracted from uploaded PDF '{file_name}':\n{extracted}"})
            st.session_state["uploaded_docs"].append(file_name)
            st.session_state["uploaded_texts"][file_name] = extracted
            st.rerun()

    if st.session_state["uploaded_docs"]:
        preview_html = "<div id='right-panel'><h4>📄 Uploaded Docs</h4>"
        for doc in st.session_state["uploaded_docs"]:
            preview_html += f"<b>📘 {doc}</b><div class='pdf-preview'>{st.session_state['uploaded_texts'][doc][:3000]}</div>"
        preview_html += "</div>"
        st.markdown(preview_html, unsafe_allow_html=True)

    def format_chat_history():
        lines = []
        for msg in st.session_state["messages"][1:]:
            prefix = "🧑" if msg["role"] == "user" else "🤖"
            lines.append(f"{prefix}: {msg['parts']}")
        return "\n\n".join(lines)

    with st.expander("📤 Export Chat", expanded=False):
        export_format = st.selectbox("Choose format:", ["Text (.txt)", "PDF (.pdf)"])
        chat_text = format_chat_history()

        if export_format == "Text (.txt)":
            st.download_button("📥 Download Chat as TXT", data=chat_text, file_name="vd_chat_history.txt", mime="text/plain")

        elif export_format == "PDF (.pdf)":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            for line in chat_text.split("\n"):
                pdf.multi_cell(0, 10, line)
            pdf_buffer = io.BytesIO()
            pdf.output(pdf_buffer)
            pdf_buffer.seek(0)
            st.download_button("📥 Download Chat as PDF", data=pdf_buffer, file_name="vd_chat_history.pdf", mime="application/pdf")

# --- Run App ---
if st.session_state.page == "home":
    home()
else:
    show_chat()

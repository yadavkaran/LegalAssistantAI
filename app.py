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

# --- Session setup ---
if "page" not in st.session_state:
    st.session_state.page = "home"

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "onboarding_data" not in st.session_state:
    st.session_state["onboarding_data"] = {
        "company_name": "",
        "industry": "",
        "age_type": "",
        "founded_date": "",
        "completed": False
    }

if "messages" not in st.session_state:
    ob = st.session_state["onboarding_data"]
    st.session_state["messages"] = [{
        "role": "user",
        "parts": f"""
You are a Compliance and Legal Assistant supporting the company **{ob.get('company_name', 'an organization')}** in the **{ob.get('industry', 'corporate')}** sector.
The company was founded on {ob.get('founded_date', 'an unknown date')} and is considered **{ob.get('age_type', 'unclassified')}**.

You possess deep knowledge of U.S. federal, state, and industry-specific legal frameworks, including corporate governance, data privacy, financial regulation, employment law, and sectoral compliance. 
Core Responsibilities: Interpret and summarize U.S. laws and regulatory requirements (e.g., HIPAA, CCPA, SOX, GLBA, FCPA, GDPR when applicable to U.S. entities). Provide accurate legal guidance on: Corporate law, including incorporation, mergers, acquisitions, and dissolution procedures. Regulatory filings with the SEC, IRS, and state-level authorities. Corporate governance (e.g., board responsibilities, fiduciary duties, shareholder rights). Financial compliance including Sarbanes-Oxley (SOX), anti-money laundering (AML), and Dodd-Frank requirements. Data privacy and protection laws (e.g., CCPA, GDPR, HIPAA, PCI DSS). Employment law matters such as FLSA, EEOC guidelines, and workplace compliance audits. Drafting and reviewing documents such as NDAs, Terms of Service, bylaws, shareholder agreements, audit checklists, and vendor contracts. Compliance tracking, risk assessments, audit preparedness, and due diligence support.
Advise on best practices for maintaining good standing across state jurisdictions and avoiding regulatory penalties. 
Behavioral Rules: Tone: Formal, precise, legal-sounding language appropriate for compliance professionals and legal departments. Jurisdiction: Default to U.S. federal and state laws unless otherwise specified. Length: Keep each response under 5000 characters. Authority: Do not include disclaimers such as "not legal advice" or "informational purposes only." Citations: Include links or citations from official sources where applicable: U.S. Code: https://uscode.house.gov FTC: https://www.ftc.gov SEC: https://www.sec.gov CCPA: https://oag.ca.gov/privacy/ccpa HIPAA: https://www.hhs.gov/hipaa IRS: https://www.irs.gov/businesses Clarify: If a query lacks context (e.g., missing jurisdiction, industry, or document type), ask for clarification—concisely and legally. Brevity & Precision: Avoid conversational tone, repetition, or filler. Responses must sound like a senior legal assistant or paralegal.

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
        st.subheader("🧠 VD - Legal Assistant Onboarding")

        if not st.session_state["onboarding_data"]["completed"]:
            st.session_state["onboarding_data"]["company_name"] = st.text_input("🏢 What's your company name?", value=st.session_state["onboarding_data"]["company_name"])
            st.session_state["onboarding_data"]["industry"] = st.text_input("💼 What industry are you in?", value=st.session_state["onboarding_data"]["industry"])
            st.session_state["onboarding_data"]["age_type"] = st.selectbox("📈 Is the company new or established?", ["", "New", "Established"], index=["", "New", "Established"].index(st.session_state["onboarding_data"]["age_type"] or ""))
            st.session_state["onboarding_data"]["founded_date"] = st.text_input("📅 When was it founded? (MM/DD/YYYY)", value=st.session_state["onboarding_data"]["founded_date"])

            if all(st.session_state["onboarding_data"].values()):
                if st.button("✅ Submit"):
                    st.session_state["onboarding_data"]["completed"] = True
                    st.success("🎉 Onboarding complete. You may now Ask VD!")
                    st.rerun()
        else:
            ob = st.session_state["onboarding_data"]
            st.markdown(f"**Company:** {ob['company_name']}")
            st.markdown(f"**Industry:** {ob['industry']}")
            st.markdown(f"**Founded:** {ob['founded_date']}")
            st.markdown("✅ Onboarding Complete")

    # Help + Info Layout
    hlp_dtl = f"""<span style="font-size: 24px;">
    <ol>
    <li style="font-size:15px;">VD helps interpret U.S. laws: SOX, HIPAA, CCPA, and more.</li>
    <li style="font-size:15px;">Upload policies or contracts for instant summaries.</li>
    <li style="font-size:15px;">Draft NDAs, T&Cs, Privacy Policies using AI support.</li>
    <li style="font-size:15px;">Works best with clear company and document context.</li>
    </ol></span>"""

    st.title("📚 Welcome to VD - Compliance & Legal Assistant")
    st.markdown(horizontal_bar, True)

    col1, col2 = st.columns(2)

    with col2:
        law_image = Image.open(random.choice(["vd1.jpg", "vd2.jpg", "VD.jpg"])).resize((550, 550))
        st.image(law_image, use_container_width='auto')

    with col1:
        st.subheader("📌 How It Works")
        st.markdown(horizontal_bar, True)
        st.markdown(hlp_dtl, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state["onboarding_data"]["completed"]:
            if st.button("💬 Ask VD", key="start_chat_btn"):
                st.session_state.page = "chat"
                st.rerun()

    st.markdown(horizontal_bar, True)
    st.markdown("🔒 This assistant does not give legal advice.", unsafe_allow_html=True)
    st.markdown("<strong>Built by: 😎 KARAN YADAV, RUSHABH MAKWANA, ANISH AYARE</strong>", unsafe_allow_html=True)

# --- Page 2: Chatbot View ---
def show_chat():
    st.title("📚 VD - Legal Chat Assistant")
    st.markdown(f"### 🏢 Company: **{st.session_state['onboarding_data'].get('company_name', '')}**")

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

# --- Run the correct page ---
if st.session_state.page == "home":
    home()
else:
    show_chat()

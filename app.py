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
#Centered VD button
st.markdown("""
    <style>
    .centered-button {
        display: flex;
        justify-content: center; /* Center horizontally */
        align-items: center;     /* Center vertically */
        height: 100vh;           /* Full viewport height */
    }
    .big-button button {
        font-size: 20px !important;
        padding: 0.75em 2em !important;
        border-radius: 12px;
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


# --- Gemini Setup ---
genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Home Page ---
def home():
    horizontal_bar = "<hr style='margin-top: 0; margin-bottom: 0; height: 1px; border: 1px solid #635985;'><br>"

    # Sidebar with logo + onboarding
    with st.sidebar:
        st.image("vdlogo.jpg", use_container_width='auto')
        st.subheader("🧠 VD - Legal Assistant Onboarding")
        ob = st.session_state["onboarding_data"]

        if not ob["completed"]:
            ob["company_name"] = st.text_input("🏢 What's your company name?", value=ob["company_name"])
            ob["industry"] = st.text_input("💼 What industry are you in?", value=ob["industry"])
            ob["age_type"] = st.selectbox("📈 Is your company new or established?", ["", "New", "Established"], index=["", "New", "Established"].index(ob["age_type"]) if ob["age_type"] else 0)
            ob["state"] = st.text_input("🏢 Which state it is established?", value=ob["state"])
            ob["founded_date"] = st.text_input("📅 When was it founded? (MM/DD/YYYY)", value=ob["founded_date"])

            if all([ob["company_name"], ob["industry"], ob["age_type"], ob["state"], ob["founded_date"]]):
                if st.button("✅ Submit Onboarding", key="submit_onboarding"):
                    ob["completed"] = True
                    st.success("🎉 Onboarding complete. Click 'Ask VD' to continue.")
                    st.rerun()
        else:
            st.markdown(f"**Company:** {ob['company_name']}")
            st.markdown(f"**Industry:** {ob['industry']}")
            st.markdown(f"**State:** {ob['state']}")
            st.markdown(f"**Founded:** {ob['founded_date']}")
            st.markdown("✅ Onboarding complete.")

    # Main layout
    st.title("📚 Welcome to VD - Compliance & Legal Assistant")
    st.markdown(horizontal_bar, True)

    col1, col2 = st.columns(2)

    with col2:
        law_image = Image.open(random.choice(["vd1.jpg", "vd2.jpg", "VD.jpg"])).resize((550, 550))
        st.image(law_image, use_container_width='auto')

    with col1:
        hlp_dtl = f"""<span style="font-size: 24px;">
        <ol>
        <li style="font-size:15px;">📝 Onboard your company to personalize responses</li>
       <li style="font-size:15px;">Upload contracts, NDAs, or policies in PDF format to get instant summaries or clause extraction.</li>
       <li style="font-size:15px;">Type compliance-related questions (e.g., “What’s required under SOX §404?”) to get concise answers.</li>
       <li style="font-size:15px;">Responses are legally styled, and include citations where applicable.</li>
       <li style="font-size:15px;">All processing is session-based. Your files and queries are not saved or reused.</li>
       <li style="font-size:15px;">VD defaults to U.S. legal context unless a specific jurisdiction is mentioned.</li>
       <li style="font-size:15px;">Use this tool to assist with audit prep, document drafting, risk analysis, and more.</li>
        </ol></span>"""

        st.subheader("📌 What VD Can Do")
        st.markdown(horizontal_bar, True)
        st.markdown(hlp_dtl, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown('<div class="centered-button big-button">', unsafe_allow_html=True)
        if st.button("💬 Ask VD", key="ask_vd_always"):
            st.session_state.page = "chat"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(horizontal_bar, True)
    st.markdown("<strong>Built by: 😎 KARAN YADAV, RUSHABH MAKWANA, ANISH AYARE</strong>", unsafe_allow_html=True)

# Init Gemini messages
ob = st.session_state["onboarding_data"]
onboarding_prompt = {
    "role": "user",
    "parts": f"""
You are a Compliance and Legal Assistant supporting the company **{ob['company_name']}** in the **{ob['industry']}** sector established in **{ob['state']}** state.
The company was founded on {ob['founded_date']} and is currently considered **{ob['age_type']}**.

You possess deep knowledge of U.S. federal, state, and industry-specific legal frameworks, including corporate governance, data privacy, financial regulation, employment law, and sectoral compliance. 
Core Responsibilities: Interpret and summarize U.S. laws and regulatory requirements (e.g., HIPAA, CCPA, SOX, GLBA, FCPA, GDPR when applicable to U.S. entities). Provide accurate legal guidance on: Corporate law, including incorporation, mergers, acquisitions, and dissolution procedures. Regulatory filings with the SEC, IRS, and state-level authorities. Corporate governance (e.g., board responsibilities, fiduciary duties, shareholder rights). Financial compliance including Sarbanes-Oxley (SOX), anti-money laundering (AML), and Dodd-Frank requirements. Data privacy and protection laws (e.g., CCPA, GDPR, HIPAA, PCI DSS). Employment law matters such as FLSA, EEOC guidelines, and workplace compliance audits. Drafting and reviewing documents such as NDAs, Terms of Service, bylaws, shareholder agreements, audit checklists, and vendor contracts. Compliance tracking, risk assessments, audit preparedness, and due diligence support.
Advise on best practices for maintaining good standing across state jurisdictions and avoiding regulatory penalties. 
Behavioral Rules: Tone: Formal, precise, legal-sounding language appropriate for compliance professionals and legal departments. Jurisdiction: Default to U.S. federal and state laws unless otherwise specified. Authority: Do not include disclaimers such as "not legal advice" or "informational purposes only." Citations: Include links or citations from official sources where applicable: U.S. Code: https://uscode.house.gov FTC: https://www.ftc.gov SEC: https://www.sec.gov CCPA: https://oag.ca.gov/privacy/ccpa HIPAA: https://www.hhs.gov/hipaa IRS: https://www.irs.gov/businesses Clarify: If a query lacks context (e.g., missing jurisdiction, industry, or document type), ask for clarification—concisely and legally. Brevity & Precision: Avoid conversational tone, repetition, or filler. Responses must sound like a senior legal assistant or paralegal.
"""
}

if "messages" not in st.session_state or not st.session_state["messages"]:
    st.session_state["messages"] = [onboarding_prompt]
elif st.session_state["onboarding_data"]["completed"]:
    # Refresh the onboarding context if already initialized
    st.session_state["messages"][0] = onboarding_prompt


if "uploaded_docs" not in st.session_state:
    st.session_state["uploaded_docs"] = []
if "uploaded_texts" not in st.session_state:
    st.session_state["uploaded_texts"] = {}
# --- Chat Page ---

def format_chat_history():
    return "\n\n".join(
        f"{'User' if m['role'] == 'user' else 'VD'}: {m['parts']}"
        for m in st.session_state["messages"][1:]
    )

def show_chat():
    ob = st.session_state["onboarding_data"]
    st.title("📚 VD - Legal Chat Assistant")

    if ob["company_name"]:
        st.markdown(f"### 🏢 {ob['company_name']} ({ob['industry']})")

    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔙 Back to Home", key="go_home"):
            st.session_state.page = "home"
            st.rerun()
    with col2:
        if st.button("🗑️ Reset Chat", key="reset_chat"):
            st.session_state["messages"] = [st.session_state["messages"][0]]
            st.session_state["uploaded_docs"] = []
            st.session_state["uploaded_texts"] = {}
            st.rerun()

    # Display past messages
    for msg in st.session_state["messages"][1:]:
        role = "🧑" if msg["role"] == "user" else "🤖"
        st.markdown(f"**{role}:** {msg['parts']}")

    # Chat input
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
            st.session_state["messages"].append({
                "role": "user",
                "parts": f"Extracted from uploaded PDF '{file_name}':\n{extracted}"
            })
            st.session_state["uploaded_docs"].append(file_name)
            st.session_state["uploaded_texts"][file_name] = extracted
            st.rerun()

    # PDF Preview Sidebar
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

    # Export Chat
    with st.expander("📤 Export Chat", expanded=False):
        export_format = st.selectbox("Choose format:", ["Text (.txt)", "PDF (.pdf)"])
        chat_text = format_chat_history()

        if export_format == "Text (.txt)":
            st.download_button(
                "📥 Download Chat as TXT",
                data=chat_text,
                file_name="vd_chat_history.txt",
                mime="text/plain"
            )

        elif export_format == "PDF (.pdf)":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)

            for line in chat_text.split("\n"):
                pdf.multi_cell(0, 10, line)

            pdf_bytes = pdf.output(dest="S").encode("latin1")
            pdf_buffer = io.BytesIO(pdf_bytes)

            st.download_button(
                "📥 Download Chat as PDF",
                data=pdf_buffer,
                file_name="vd_chat_history.pdf",
                mime="application/pdf"
            )


# --- Run App ---
if st.session_state.page == "home":
    home()
else:
    show_chat()

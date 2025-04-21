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

# --- State Setup ---
if "page" not in st.session_state:
    st.session_state.page = "home"

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Onboarding storage
if "onboarding_data" not in st.session_state:
    st.session_state["onboarding_data"] = {
        "company_name": "",
        "industry": "",
        "age_type": "",
        "founded_date": "",
        "completed": False
    }

# Gemini messages (initialized after onboarding)
if "messages" not in st.session_state:
    ob = st.session_state["onboarding_data"]
    st.session_state["messages"] = [{
        "role": "user",
        "parts": f"""
You are a Compliance and Legal Assistant supporting the company **{ob['company_name']}** in the **{ob['industry']}** sector.
The company was founded on {ob['founded_date']} and is currently considered **{ob['age_type']}**.

You help interpret U.S. laws and regulatory requirements (e.g., HIPAA, SOX, CCPA, PCI DSS).
Keep responses under 200 characters. Use legal-sounding, precise tone. Default to U.S. law.

Cite official sources where applicable.
"""
    }]

if "uploaded_docs" not in st.session_state:
    st.session_state["uploaded_docs"] = []

if "uploaded_texts" not in st.session_state:
    st.session_state["uploaded_texts"] = {}

# --- Gemini setup ---
genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Home Page with Onboarding ---
def home():
    horizontal_bar = "<hr style='margin-top: 0; margin-bottom: 0; height: 1px; border: 1px solid #635985;'><br>"

    with st.sidebar:
        st.subheader("🧠 VD - Legal Assistant Onboarding")
        ob = st.session_state["onboarding_data"]

        if not ob["completed"]:
            ob["company_name"] = st.text_input("🏢 What's your company name?", value=ob["company_name"])
            ob["industry"] = st.text_input("💼 What industry are you in?", value=ob["industry"])
            ob["age_type"] = st.selectbox("📈 Is your company new or established?", ["", "New", "Established"], index=["", "New", "Established"].index(ob["age_type"]) if ob["age_type"] else 0)
            ob["founded_date"] = st.text_input("📅 When was it founded? (MM/DD/YYYY)", value=ob["founded_date"])

            if all([ob["company_name"], ob["industry"], ob["age_type"], ob["founded_date"]]):
                if st.button("✅ Submit Onboarding", key="submit_onboarding"):
                    ob["completed"] = True
                    st.success("🎉 Onboarding complete. Click 'Ask VD' to continue.")
                    st.rerun()
        else:
            st.markdown(f"**Company:** {ob['company_name']}")
            st.markdown(f"**Industry:** {ob['industry']}")
            st.markdown(f"**Founded:** {ob['founded_date']}")
            st.markdown("✅ Onboarding complete.")

    # Main Landing Page Layout
    st.title("📚 Welcome to VD - Compliance & Legal Assistant")
    st.markdown(horizontal_bar, True)

    col1, col2 = st.columns(2)

    with col2:
        law_image = Image.open(random.choice(["vd1.jpg", "vd2.jpg", "VD.jpg"])).resize((550, 550))
        st.image(law_image, use_container_width='auto')

    with col1:
        hlp_dtl = f"""<span style="font-size: 24px;">
        <ol>
        <li style="font-size:15px;">Interpret U.S. corporate and privacy laws.</li>
        <li style="font-size:15px;">Upload legal PDFs for instant analysis.</li>
        <li style="font-size:15px;">Draft NDAs, Terms, and other documents.</li>
        <li style="font-size:15px;">Responses under 200 characters. No filler. Precise legal tone.</li>
        </ol></span>"""

        st.subheader("📌 What VD Can Do")
        st.markdown(horizontal_bar, True)
        st.markdown(hlp_dtl, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state["onboarding_data"]["completed"]:
            if st.button("💬 Ask VD", key="ask_vd"):
                st.session_state.page = "chat"
                st.rerun()

    st.markdown(horizontal_bar, True)
    st.markdown("🔒 This AI assistant does not give legal advice.", unsafe_allow_html=True)
    st.markdown("<strong>Built by: 😎 KARAN YADAV, RUSHABH MAKWANA, ANISH AYARE</strong>", unsafe_allow_html=True)

# --- Chat Page ---
def show_chat():
    ob = st.session_state["onboarding_data"]
    st.title("📚 VD - Legal Chat Assistant")
    if ob["company_name"]:
        st.markdown(f"### 🏢 {ob['company_name']} ({ob['industry']})")

    if st.button("🔙 Back to Home", key="go_home"):
        st.session_state.page = "home"
        st.rerun()

    if st.button("🗑️ Reset Chat", key="reset_chat"):
        st.session_state["messages"] = [st.session_state["messages"][0]]
        st.session_state["uploaded_docs"] = []
        st.session_state["uploaded_texts"] = {}
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

            os.makedirs("logs", exist_ok=True)
            with open(f"logs/{st.session_state['user_id']}.txt", "a", encoding="utf-8") as f:
                f.write(f"\nUser: {user_input}\nBot: {response.text}\n")

            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")

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

# --- Run App ---
if st.session_state.page == "home":
    home()
else:
    show_chat()

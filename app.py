import streamlit as st
import google.generativeai as genai
import dotenv
import os

# Load environment variables from .env
dotenv.load_dotenv()
api_key = os.getenv("API_KEY")

# Configure the Gemini model
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to generate a response from Gemini
def generate_response(messages):
    try:
        response = model.generate_content(messages)
        return response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize chat history in session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
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
        }
    ]

# App title
st.title("🧑‍⚖️ Compliance & Legal Assistant")

# Chat display (history)
for message in st.session_state.messages[1:]:  # Skip system prompt
    if message["role"] == "user":
        st.markdown(f"**You:** {message['parts']}")
    else:
        st.markdown(f"**Assistant:** {message['parts']}")

# Divider and input at the bottom
st.markdown("---")

# Text input box at the bottom
user_input = st.text_area("Type your legal or compliance question:", height=100)

# Button to send input
if st.button("Send"):
    if user_input.strip():
        st.session_state.messages.append({"role": "user", "parts": user_input})
        with st.spinner("Thinking..."):
            bot_response = generate_response(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "parts": bot_response})
        st.experimental_rerun()  # Refresh the app to show new messages

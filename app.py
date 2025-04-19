import streamlit as st
import google.generativeai as genai

# Load API key securely from Streamlit secrets
api_key = st.secrets["API_KEY"]

# Configure the Gemini model
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-pro")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("💬 Gemini Chatbot")

user_input = st.text_input("You:")

if user_input:
    st.session_state["messages"].append({"role": "user", "parts": user_input})
    try:
        response = model.generate_content(st.session_state["messages"])
        st.session_state["messages"].append({"role": "model", "parts": response.text})
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Display chat history
for msg in st.session_state["messages"]:
    who = "🧑" if msg["role"] == "user" else "🤖"
    st.markdown(f"**{who}:** {msg['parts']}")

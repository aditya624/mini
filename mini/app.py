import os
import streamlit as st
from uuid import uuid4
from mini.agent.agent import Agent

@st.cache_resource
def get_agent(
    gemini_api_key, 
    serper_api_key
):
    return Agent(gemini_api_key=gemini_api_key, serper_api_key=serper_api_key)

def get_session_id():
    session_id = str(uuid4())
    return session_id

with st.sidebar:
    gemini_api_key = st.text_input("Gemini API Key", key="gemini_api_key", type="password", value="")
    serper_api_key = st.text_input("Serper API Key", key="serper_api_key", type="password", value="")

st.sidebar.info(
    """
    1. Get your Gemini API keys from [aistudio](https://aistudio.google.com/)
    2. Add your Serper API keys from [serper](https://serper.dev/)
    """
)

agent = get_agent(
    gemini_api_key=gemini_api_key,
    serper_api_key=serper_api_key
)

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by Gemini, Google Search and Arvix")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

if "session_id" not in st.session_state:
    st.session_state.session_id = get_session_id()

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not os.getenv("GEMINI_API_KEY") or not os.getenv("SERPER_API_KEY"):
        st.info("Please add your Groq API key and Serper API key to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    answer = agent.ask(prompt, st.session_state.session_id)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
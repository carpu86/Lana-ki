import streamlit as st
import os
from datetime import datetime

st.set_page_config(
    page_title="Lana KI - Schaltzentrale",
    page_icon="\U0001F916",
    layout="wide"
)

st.title("Lana KI - Private Schaltzentrale")
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
host_str = os.uname().nodename
st.markdown(f"**Host:** `{host_str}` | **Zeit:** `{now_str}`")
st.markdown("---")

with st.sidebar:
    st.header("System-Status")
    st.success("KI-Core: Online")
    venv_path = os.environ.get("VIRTUAL_ENV", "Nicht aktiv")
    st.info(f"Python-Umgebung: {venv_path}")
    st.header("Aktionen")
    if st.button("System-Check"):
        st.toast("System-Check gestartet...", icon="\u2699\uFE0F")

st.header("Chat mit Lana")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hallo Thomas, ich bin bereit. Was liegt an?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Deine Nachricht an Lana..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    response = "Lana verarbeitet: " + prompt
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

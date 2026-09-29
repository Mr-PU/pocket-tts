import sys
from pathlib import Path

# Allow importing the "app" package that sits at the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app import config
from app.graph import build_graph

SYSTEM_PROMPT = (
    "You are a helpful voice assistant. Keep answers concise and "
    "conversational, since they will be spoken out loud."
)

st.set_page_config(page_title="Local Voice Agent", page_icon="🎙️", layout="centered")

st.title("🎙️ Local Voice Agent")

provider_label = (
    f"`{config.OLLAMA_MODEL}` via Ollama"
    if config.LLM_PROVIDER == "ollama"
    else f"`{config.OPENAI_MODEL}` via OpenAI"
)
st.caption(f"LLM: {provider_label} · TTS: Pocket TTS (`{config.TTS_VOICE}`)")


@st.cache_resource(show_spinner="Loading agent (first request also downloads the TTS model)...")
def get_app():
    return build_graph()


if "history" not in st.session_state:
    st.session_state.history = [SystemMessage(content=SYSTEM_PROMPT)]
if "audio_paths" not in st.session_state:
    st.session_state.audio_paths = {}

# Render past turns
for i, msg in enumerate(st.session_state.history[1:], start=1):
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)
            audio_path = st.session_state.audio_paths.get(i)
            if audio_path and Path(audio_path).exists():
                st.audio(audio_path)

user_input = st.chat_input("Say something...")

if user_input:
    st.session_state.history.append(HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and generating speech..."):
            agent_app = get_app()
            result = agent_app.invoke(
                {"messages": st.session_state.history, "audio_path": ""}
            )
        st.session_state.history = result["messages"]
        ai_index = len(st.session_state.history) - 1
        st.session_state.audio_paths[ai_index] = result["audio_path"]

        ai_msg = st.session_state.history[-1]
        st.write(ai_msg.content)
        st.audio(result["audio_path"])

with st.sidebar:
    st.header("Settings")
    st.write(f"**Provider:** {config.LLM_PROVIDER}")
    st.write(f"**Voice:** `{config.TTS_VOICE}`")
    st.write(f"**Language:** `{config.TTS_LANGUAGE}`")
    st.caption("Change these in your `.env` file and restart the UI container.")
    if st.button("Clear conversation"):
        st.session_state.history = [SystemMessage(content=SYSTEM_PROMPT)]
        st.session_state.audio_paths = {}
        st.rerun()

import os
import streamlit as st
from dotenv import load_dotenv
from m1_p2_meeting_agent import render_meeting_agent
from m1_p7_event_agent import render_event_agent

load_dotenv()

st.set_page_config(
    page_title="Agentic AI - Project 01 (M1-P2 & M1-P7)",
    page_icon="🤖",
    layout="wide"
)

st.sidebar.title("🤖 Agentic AI — Project 01")
st.sidebar.markdown("**Submission (40M) + Viva (10M)**")
st.sidebar.divider()

api_key_input = st.sidebar.text_input(
    "🔑 Gemini API Key",
    value=os.getenv("GEMINI_API_KEY", ""),
    type="password",
    help="Get a free key from https://aistudio.google.com/ or enable Offline Viva Demo Mode below."
)

demo_mode = st.sidebar.toggle(
    "⚡ Offline Viva Demo Mode (No API Key Needed)",
    value=not bool(api_key_input),
    help="Uses deterministic pre-computed agent states if API key is missing or Wi-Fi is unavailable during viva."
)

st.sidebar.divider()
selected_project = st.sidebar.radio(
    "📂 Select Project to Run:",
    [
        "M1-P2: Meeting-to-Action Assistant",
        "M1-P7: Autonomous Event Planning Agent"
    ]
)

st.sidebar.divider()
with st.sidebar.expander("🎓 Viva Architecture Highlights"):
    st.markdown("""
    - **SDK**: `google-genai` (`gemini-2.5-flash`)
    - **Structured Output**: Pydantic `BaseModel` schema enforcement
    - **M1-P2 Pattern**: Multi-Step Extraction + Ambiguity Critic + Human-in-the-Loop (HITL) Resolution
    - **M1-P7 Pattern**: Hierarchical Goal Decomposition + Stateful Memory (`st.session_state`) + Autonomous Task Drafter
    """)

if selected_project == "M1-P2: Meeting-to-Action Assistant":
    render_meeting_agent(api_key=api_key_input, demo_mode=demo_mode)
else:
    render_event_agent(api_key=api_key_input, demo_mode=demo_mode)

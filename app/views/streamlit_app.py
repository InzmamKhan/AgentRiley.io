import streamlit as st
import requests
import os
import json
from pathlib import Path
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Agent Riley | Tactical Recon RAG",
    page_icon="💀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")

# Dark Neumorphic & Call of Duty Special Ops Styling
TACTICAL_NEUMORPHIC_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:ital,wght@0,300;0,500;0,700;1,400&family=Share+Tech+Mono&display=swap');

:root {
    --bg-base: #141619;
    --neu-dark: #0e0f11;
    --neu-light: #1b1e22;
    --accent-green: #39ff14;
    --accent-amber: #ffaa00;
    --accent-red: #ff3333;
    --text-primary: #e2e8f0;
    --text-muted: #8892b0;
    --border-color: #262c33;
}

/* Overall page background */
.stApp {
    background-color: var(--bg-base);
    font-family: 'Chakra Petch', sans-serif;
    color: var(--text-primary);
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Chakra Petch', sans-serif;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #121417 !important;
    border-right: 1px solid #1f242b;
}

/* Dark Neumorphic Container Card */
.neu-card {
    background: #141619;
    border-radius: 14px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 6px 6px 14px var(--neu-dark), -6px -6px 14px var(--neu-light);
    border: 1px solid rgba(255, 255, 255, 0.03);
}

/* Inset Neumorphic Card (Recessed display) */
.neu-inset {
    background: #111316;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: inset 4px 4px 8px #0a0b0d, inset -4px -4px 8px #181b1f;
    border: 1px solid rgba(0, 0, 0, 0.5);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.88rem;
}

/* Tactical HUD Header */
.tactical-hud {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #232830;
    padding-bottom: 0.75rem;
    margin-bottom: 1.5rem;
}

.hud-callsign {
    color: var(--accent-green);
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    text-shadow: 0 0 10px rgba(57, 255, 20, 0.4);
}

.hud-status {
    background: #121518;
    color: var(--accent-amber);
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    letter-spacing: 1px;
    box-shadow: inset 2px 2px 4px #0a0b0d, inset -2px -2px 4px #1a1e23;
    border: 1px solid rgba(255, 170, 0, 0.2);
}

/* Custom Tactical Buttons */
div.stButton > button {
    background: #16181d !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    border: 1px solid #262c33 !important;
    box-shadow: 4px 4px 10px #0a0b0d, -4px -4px 10px #1e2227 !important;
    font-family: 'Chakra Petch', sans-serif !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    transition: all 0.2s ease-in-out !important;
}

div.stButton > button:hover {
    box-shadow: 2px 2px 5px #0a0b0d, -2px -2px 5px #1e2227 !important;
    color: var(--accent-green) !important;
    border-color: var(--accent-green) !important;
    text-shadow: 0 0 8px rgba(57, 255, 20, 0.4) !important;
}

div.stButton > button:active {
    box-shadow: inset 3px 3px 6px #0a0b0d, inset -3px -3px 6px #1e2227 !important;
}

/* Chat Input Styling */
[data-testid="stChatInput"] textarea {
    background-color: #121417 !important;
    color: #39ff14 !important;
    border-radius: 12px !important;
    border: 1px solid #262c33 !important;
    box-shadow: inset 3px 3px 7px #090a0c, inset -3px -3px 7px #1c1f24 !important;
    font-family: 'Share Tech Mono', monospace !important;
}

/* Chat Message Bubbles */
.chat-bubble-user {
    background: #15181c;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    box-shadow: 5px 5px 12px #0a0b0d, -5px -5px 12px #1c2025;
    border-left: 4px solid #4a5568;
}

.chat-bubble-agent {
    background: #121418;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    box-shadow: 5px 5px 12px #090a0d, -5px -5px 12px #1a1e23;
    border-left: 4px solid var(--accent-green);
    position: relative;
}

.intel-badge {
    background: #1a1e24;
    color: var(--accent-amber);
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    margin-right: 0.5rem;
    box-shadow: inset 1px 1px 3px #0b0c0e;
}
</style>
"""

st.markdown(TACTICAL_NEUMORPHIC_CSS, unsafe_allow_html=True)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Operator, this is Simon 'Ghost' Riley [Bravo 0-7]. Perimeter secured. Drop your tactical files (CSV, Excel, Word, PDF) into the `documents/` drop zone, and I'll extract all mission-critical intel on your mark. Awaiting orders.",
            "sources": []
        }
    ]

# Fetch stats helper
def fetch_stats():
    try:
        res = requests.get(f"{BACKEND_URL}/stats", timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

stats = fetch_stats()

# ----------------- SIDEBAR COMMAND CENTER -----------------
with st.sidebar:
    st.markdown("""
        <div class="neu-card" style="text-align: center;">
            <div style="font-size: 2.8rem;">💀</div>
            <h3 style="margin: 0; color: #fff;">TASK FORCE 141</h3>
            <div style="color: #39ff14; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem;">CALLSIGN: GHOST / RILEY</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🛰️ Drop Zone Intel")
    
    if stats:
        tot_docs = stats.get("total_documents", 0)
        tot_chunks = stats.get("total_chunks", 0)
        files = stats.get("disk_files", []) or stats.get("document_files", [])
        
        st.markdown(f"""
            <div class="neu-inset">
                <div>[STATUS] <b>ACTIVE RADAR</b></div>
                <div>[DROP FILES] <b>{len(files)} Secure Files</b></div>
                <div>[VEC CHUNKS] <b>{tot_chunks} Vectors</b></div>
            </div>
        """, unsafe_allow_html=True)
        
        if files:
            st.markdown("<p style='font-size:0.8rem; color:#8892b0; margin-top:10px;'>RECON FILES IN DROP ZONE:</p>", unsafe_allow_html=True)
            for f in files:
                st.markdown(f"<div style='font-family:monospace; font-size:0.75rem; color:#a0aec0;'>📁 {f}</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="neu-inset" style="color: #ffaa00;">
                [COMMS ALERT] Backend not detected on :8000.<br/>
                Start FastAPI via `python -m app.main`.
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚡ Direct Air Drop")
    uploaded_files = st.file_uploader(
        "Deposit CSV, Excel, Word, PDF", 
        type=["csv", "xlsx", "xls", "docx", "pdf", "txt", "md"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("🚀 INGEST DROPPED INTEL"):
            with st.spinner("Encrypting & indexing files into FAISS..."):
                files_payload = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
                try:
                    res = requests.post(f"{BACKEND_URL}/upload", files=files_payload, timeout=60)
                    if res.status_code == 200:
                        st.success("Air drop secured and indexed!")
                        st.rerun()
                    else:
                        st.error(f"Air drop failed: {res.text}")
                except Exception as e:
                    st.error(f"Connection failure: {str(e)}")

    if st.button("🔄 RE-SCAN DROP ZONE FOLDER"):
        with st.spinner("Ghost scanning documents folder..."):
            try:
                res = requests.post(f"{BACKEND_URL}/ingest", timeout=60)
                if res.status_code == 200:
                    st.success("Folder rescan complete!")
                    st.rerun()
                else:
                    st.error(f"Rescan error: {res.text}")
            except Exception as e:
                st.error(f"Scan failed: {str(e)}")

    if st.button("🗑️ CLEAR INTEL LOG"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Intel log cleared. Ready for the next tactical briefing.",
                "sources": []
            }
        ]
        st.rerun()

# ----------------- MAIN TACTICAL HUD -----------------
st.markdown("""
    <div class="tactical-hud">
        <div>
            <div class="hud-callsign">AGENT RILEY // TACTICAL RAG SYSTEM</div>
            <div style="font-size: 0.8rem; color: #718096; letter-spacing: 1px;">TASK FORCE 141 • NVIDIA NIM POWERED • LOCAL DEPLOYMENT</div>
        </div>
        <div class="hud-status">● MISSION READY</div>
    </div>
""", unsafe_allow_html=True)

# Display Chat History
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
            <div class="chat-bubble-user">
                <div style="font-size: 0.75rem; color: #718096; margin-bottom: 4px; font-family: 'Share Tech Mono', monospace;">[OPERATOR DIRECTIVE]</div>
                <div>{msg["content"]}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        sources_html = ""
        if msg.get("sources"):
            sources_html = "<div style='margin-top: 10px; border-top: 1px dashed #2d3748; padding-top: 8px;'><span style='font-size:0.75rem; color:#ffaa00; font-family:monospace;'>[RECOVERED SOURCES]: </span>"
            for s in msg["sources"]:
                sources_html += f"<span class='intel-badge'>📄 {s['source']} (Match: {s['score']})</span> "
            sources_html += "</div>"

        st.markdown(f"""
            <div class="chat-bubble-agent">
                <div style="font-size: 0.75rem; color: #39ff14; margin-bottom: 4px; font-family: 'Share Tech Mono', monospace;">[BRAVO 0-7 // GHOST]</div>
                <div style="white-space: pre-wrap;">{msg["content"]}</div>
                {sources_html}
            </div>
        """, unsafe_allow_html=True)

# User Query Input
if prompt := st.chat_input("Enter tactical query or document question for Agent Riley..."):
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# If last message was from user, process through Agent Riley backend
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_query = st.session_state.messages[-1]["content"]
    
    with st.spinner("Ghost scanning intercepted documents & computing answer..."):
        try:
            res = requests.post(
                f"{BACKEND_URL}/query",
                json={"query": user_query, "top_k": 4},
                timeout=60
            )
            if res.status_code == 200:
                data = res.json()
                answer = data.get("answer", "No intelligence returned.")
                sources = data.get("sources", [])
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"[COMMS ERROR] Backend reported status code {res.status_code}: {res.text}",
                    "sources": []
                })
        except requests.exceptions.ConnectionError:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "[OFFLINE ALERT] Unable to establish link to FastAPI Backend at http://localhost:8000. Launch backend using `python -m app.main`.",
                "sources": []
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"[SYSTEM FAILURE] Tactical error: {str(e)}",
                "sources": []
            })
    st.rerun()

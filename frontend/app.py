import streamlit as st
import requests
import time

# ── Config ────────────────────────────────────────────────────────
import os
BACKEND_URL = os.getenv("BACKEND_URL", "http://0.0.0.0:8000")
# Force session persistence
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# ── Page setup ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Vaultiq — Document Intelligence",
    page_icon="🔐",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

/* Dark background */
.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d0d1a 50%, #0a0f1a 100%);
    color: #e0e0f0;
}

/* Hide streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem; }

/* ── Hero section ── */
.hero-container {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    position: relative;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(255,45,85,0.15), rgba(255,149,0,0.15));
    border: 1px solid rgba(255,45,85,0.4);
    border-radius: 20px;
    padding: 6px 18px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #ff6b9d;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 3.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ff2d55 0%, #ff6b35 35%, #ff9500 60%, #ff2d55 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradientShift 4s ease infinite;
    line-height: 1.1;
    margin: 0;
}
@keyframes gradientShift {
    0% { background-position: 0% center; }
    50% { background-position: 100% center; }
    100% { background-position: 0% center; }
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #8888aa;
    margin: 0.8rem 0 0;
    font-weight: 400;
    letter-spacing: 0.02em;
}
.hero-subtitle span {
    color: #ff6b35;
    font-weight: 600;
}

/* ── Glowing divider ── */
.glow-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #ff2d55, #ff6b35, #ff9500, transparent);
    border: none;
    margin: 1.5rem 0;
    animation: glowPulse 3s ease infinite;
}
@keyframes glowPulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
}

/* ── Feature cards ── */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}
.feature-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.2rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.feature-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent);
    opacity: 0.8;
}
.feature-card-icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
.feature-card-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #e0e0f0;
    margin-bottom: 0.3rem;
}
.feature-card-desc { font-size: 0.78rem; color: #6666aa; line-height: 1.5; }

/* ── Upload zone ── */
.upload-zone {
    background: rgba(255,45,85,0.05);
    border: 2px dashed rgba(255,45,85,0.3);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
    margin: 1rem 0;
}
.upload-zone:hover {
    border-color: rgba(255,45,85,0.6);
    background: rgba(255,45,85,0.08);
}
.upload-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #ff6b9d;
    margin-bottom: 0.3rem;
}
.upload-sub { font-size: 0.8rem; color: #6666aa; }

/* ── Status card ── */
.status-card {
    background: linear-gradient(135deg, rgba(255,45,85,0.1), rgba(255,149,0,0.1));
    border: 1px solid rgba(255,45,85,0.3);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
}
.status-title {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #ff9500;
    margin-bottom: 0.8rem;
}
.status-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 0.4rem 0;
    font-size: 0.82rem;
}
.status-label { color: #8888aa; }
.status-value {
    color: #ff6b9d;
    font-weight: 600;
    font-family: monospace;
    font-size: 0.8rem;
}

/* ── Pulse dot ── */
.pulse-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #22c55e;
    margin-right: 6px;
    animation: pulse 2s ease infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}
.offline-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #ef4444;
    margin-right: 6px;
}

/* ── Chat messages ── */
.chat-wrapper {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 1.5rem;
    margin: 1rem 0;
    min-height: 300px;
    max-height: 500px;
    overflow-y: auto;
}
.msg-user {
    display: flex;
    justify-content: flex-end;
    margin: 0.8rem 0;
}
.msg-user-bubble {
    background: linear-gradient(135deg, #ff2d55, #ff6b35);
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 0.7rem 1.1rem;
    max-width: 70%;
    font-size: 0.9rem;
    line-height: 1.5;
    box-shadow: 0 4px 15px rgba(255,45,85,0.3);
}
.msg-ai {
    display: flex;
    justify-content: flex-start;
    margin: 0.8rem 0;
    gap: 0.6rem;
    align-items: flex-start;
}
.msg-ai-avatar {
    width: 32px; height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff2d55, #ff9500);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
    box-shadow: 0 0 12px rgba(255,45,85,0.4);
}
.msg-ai-bubble {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    color: #e0e0f0;
    border-radius: 4px 18px 18px 18px;
    padding: 0.8rem 1.1rem;
    max-width: 75%;
    font-size: 0.9rem;
    line-height: 1.6;
}
.source-chip {
    display: inline-block;
    background: rgba(255,149,0,0.15);
    border: 1px solid rgba(255,149,0,0.4);
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.72rem;
    color: #ff9500;
    margin: 0.4rem 0.2rem 0;
    font-weight: 500;
}

/* ── Section header ── */
.section-header {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #ff2d55;
    margin: 1.5rem 0 0.7rem;
}

/* ── Metric chips ── */
.metric-row {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    margin: 0.5rem 0;
}
.metric-chip {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
    color: #ccccee;
    text-align: center;
    flex: 1;
}
.metric-chip-value {
    font-size: 1.3rem;
    font-weight: 700;
    color: #ff6b35;
    display: block;
}

/* ── Streamlit overrides ── */
.stButton > button {
    background: linear-gradient(135deg, #ff2d55, #ff6b35) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(255,45,85,0.3) !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255,45,85,0.5) !important;
}
.stTextInput > div > div > input,
.stChatInputContainer textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,45,85,0.3) !important;
    border-radius: 12px !important;
    color: #e0e0f0 !important;
}
.stChatInputContainer textarea:focus {
    border-color: #ff2d55 !important;
    box-shadow: 0 0 0 2px rgba(255,45,85,0.2) !important;
}
[data-testid="stSidebar"] {
    background: rgba(10,10,20,0.95) !important;
    border-right: 1px solid rgba(255,45,85,0.15) !important;
}
[data-testid="stSidebar"] * { color: #ccccee !important; }
.stSpinner > div { border-top-color: #ff2d55 !important; }
.stSuccess {
    background: rgba(34,197,94,0.1) !important;
    border: 1px solid rgba(34,197,94,0.3) !important;
    border-radius: 10px !important;
    color: #22c55e !important;
}
.stError {
    background: rgba(239,68,68,0.1) !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    border-radius: 10px !important;
}
.stInfo {
    background: rgba(255,45,85,0.08) !important;
    border: 1px solid rgba(255,45,85,0.2) !important;
    border-radius: 10px !important;
    color: #ff6b9d !important;
}
.stFileUploader {
    background: rgba(255,255,255,0.02) !important;
    border: 2px dashed rgba(255,45,85,0.3) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
}
div[data-testid="stChatMessage"] {
    background: transparent !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] div {
    color: #e0e0f0 !important;
}
.stChatMessage p {
    color: #e0e0f0 !important;
}            
            
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────
for key, default in {
    "session_id": None,
    "filename": None,
    "chat_history": [],
    "chunk_count": 0,
    "total_questions": 0
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-header">⚡ Upload Document</div>', unsafe_allow_html=True)
    # ── Load previous session ─────────────────────────────────────
    # ── Session Manager ───────────────────────────────────────────
    st.markdown('<div class="section-header">🗂️ My Sessions</div>', unsafe_allow_html=True)
    
    try:
        registry_response = requests.get(f"{BACKEND_URL}/sessions", timeout=5)
        if registry_response.status_code == 200:
            sessions = registry_response.json().get("sessions", {})
            if sessions:
                for sid, info in sorted(sessions.items(), 
                                       key=lambda x: x[1].get("created_at", ""), 
                                       reverse=True):
                    fname = info.get("filename", "Unknown")[:20]
                    date = info.get("created_at", "")
                    chunks = info.get("chunk_count", "?")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
                        border-radius:8px;padding:8px 10px;margin-bottom:6px;">
                            <div style="font-size:0.8rem;color:#e0e0f0;font-weight:500;">📄 {fname}</div>
                            <div style="font-size:0.7rem;color:#6666aa;">{date}</div>
                            <div style="font-size:0.7rem;color:#ff9500;">{chunks} chunks · {sid}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if st.button("Load", key=f"load_{sid}"):
                            st.session_state.session_id = sid
                            st.session_state.filename = info.get("filename", f"Session {sid}")
                            st.session_state.chunk_count = chunks
                            st.session_state.chat_history = []
                            st.session_state.total_questions = 0
                            st.success(f"✅ Loaded!")
                            st.rerun()
            else:
                st.markdown('<p style="font-size:0.75rem;color:#555577;">No sessions yet. Upload a PDF!</p>', 
                           unsafe_allow_html=True)
    except:
        prev_session = st.text_input("Session ID", placeholder="e.g. 4afa2839", 
                                      label_visibility="collapsed")
        if st.button("📂 Load Session", use_container_width=True):
            if prev_session.strip():
                st.session_state.session_id = prev_session.strip()
                st.session_state.filename = f"Session {prev_session.strip()}"
                st.session_state.chat_history = []
                st.session_state.total_questions = 0
                st.session_state.chunk_count = "?"
                st.rerun()

    st.markdown("---")
    uploaded_file = st.file_uploader(
        label="Drop your PDF here",
        type=["pdf"],
        help="PDF files only | Max 10MB",
        label_visibility="collapsed"
    )

    st.markdown('<p style="font-size:0.75rem;color:#6666aa;text-align:center;margin-top:0.3rem;">PDF only · Max 10 MB</p>', unsafe_allow_html=True)

    if uploaded_file:
        if st.button("⚡ Process & Index Document"):
            with st.spinner("Indexing your document..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    response = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=60)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.session_id = data["session_id"]
                        st.session_state.filename = data["filename"]
                        st.session_state.chunk_count = data["chunk_count"]
                        st.session_state.chat_history = []
                        st.session_state.total_questions = 0
                        st.success(f"✅ Indexed {data['chunk_count']} chunks!")
                    else:
                        st.error(f"❌ {response.json().get('detail', 'Upload failed.')}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Backend offline.")
                except Exception as e:
                    st.error(f"❌ {str(e)}")

    # Status card
    if st.session_state.session_id:
        st.markdown(f"""
        <div class="status-card">
            <div class="status-title">📄 Active Document</div>
            <div class="status-row">
                <span class="status-label">File</span>
                <span class="status-value">{st.session_state.filename[:18]}...</span>
            </div>
            <div class="status-row">
                <span class="status-label">Chunks</span>
                <span class="status-value">{st.session_state.chunk_count}</span>
            </div>
            <div class="status-row">
                <span class="status-label">Session</span>
                <span class="status-value">{st.session_state.session_id}</span>
            </div>
            <div class="status-row">
                <span class="status-label">Questions</span>
                <span class="status-value">{st.session_state.total_questions}</span>
            </div>
        </div>
        <p style="font-size:0.72rem;color:#666688;text-align:center;margin-top:0.5rem;">
            💾 Save your Session ID to resume later
        </p>
        """, unsafe_allow_html=True)

        if st.button("🗑️ Clear Session"):
            for key in ["session_id", "filename", "chat_history", "chunk_count", "total_questions"]:
                st.session_state[key] = None if key == "session_id" else ([] if key == "chat_history" else 0)
            st.rerun()

    # Backend health
    st.markdown('<div class="section-header">🖥️ System</div>', unsafe_allow_html=True)
    try:
        h = requests.get(f"{BACKEND_URL}/health", timeout=3).json()
        st.markdown(f'<span class="pulse-dot"></span><span style="font-size:0.8rem;color:#22c55e;">Backend Online</span>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:0.72rem;color:#555577;margin:4px 0;">Model: all-MiniLM-L6-v2</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:0.72rem;color:#555577;">LLM: Llama3-8b · Groq</p>', unsafe_allow_html=True)
    except:
        st.markdown('<span class="offline-dot"></span><span style="font-size:0.8rem;color:#ef4444;">Backend Offline</span>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top:2rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.06);font-size:0.7rem;color:#444466;text-align:center;">Vaultiq v1.0.0 · Built with ❤️</div>', unsafe_allow_html=True)

# ── Main area ─────────────────────────────────────────────────────
st.markdown('<div class="hero-container"><div class="hero-badge">🔐 RAG-Powered Document Intelligence</div><h1 class="hero-title">VAULTIQ</h1><p class="hero-subtitle">Ask anything about your documents — powered by <span>Llama3 × LangChain × FAISS</span></p></div>', unsafe_allow_html=True)

st.markdown('<hr class="glow-divider"/>', unsafe_allow_html=True)

if not st.session_state.session_id:
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card" style="--accent: linear-gradient(135deg, #ff2d55, #ff6b35);">
            <div class="feature-card-icon">🎯</div>
            <div class="feature-card-title">Zero Hallucination</div>
            <div class="feature-card-desc">Answers grounded strictly in your document context.</div>
        </div>
        <div class="feature-card" style="--accent: linear-gradient(135deg, #ff6b35, #ff9500);">
            <div class="feature-card-icon">📑</div>
            <div class="feature-card-title">Source Citations</div>
            <div class="feature-card-desc">Every answer includes exact page references.</div>
        </div>
        <div class="feature-card" style="--accent: linear-gradient(135deg, #ff9500, #ffcc00);">
            <div class="feature-card-icon">⚡</div>
            <div class="feature-card-title">Groq Speed</div>
            <div class="feature-card-desc">Ultra-fast Llama3 inference — answers in under 3 seconds.</div>
        </div>
    </div>
    <div class="upload-zone">
        <div class="upload-title">👈 Upload a PDF from the sidebar to begin</div>
        <div class="upload-sub">research papers · contracts · reports · policy documents</div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-chip"><span class="metric-chip-value">{st.session_state.chunk_count}</span>Chunks Indexed</div>
        <div class="metric-chip"><span class="metric-chip-value">{st.session_state.total_questions}</span>Questions Asked</div>
        <div class="metric-chip"><span class="metric-chip-value">🟢</span>RAG Active</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">💬 Chat with {st.session_state.filename}</div>', unsafe_allow_html=True)

    # ── Chat history using native Streamlit ──────────────────────
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["question"])
        with st.chat_message("assistant"):
            st.write(chat["answer"])
            if chat["sources"]:
                source_html = " ".join([f'<span class="source-chip">📄 {s}</span>' for s in chat["sources"]])
                st.markdown(source_html, unsafe_allow_html=True)

    # ── Input ─────────────────────────────────────────────────────
    question = st.chat_input("Ask anything about your document...")

    if question and st.session_state.get("session_id"):
        sid = st.session_state.session_id
        with st.spinner("🔍 Searching through your document..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/query",
                    json={"question": question, "session_id": sid},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": data["answer"],
                        "sources": data["sources"]
                    })
                    st.session_state.total_questions += 1
                    st.rerun()
                else:
                    st.error(f"❌ {response.json().get('detail', 'Query failed.')}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend.")
            except Exception as e:
                st.error(f"❌ {str(e)}")

    elif question and not st.session_state.get("session_id"):
        st.error("❌ Please upload a document first!")
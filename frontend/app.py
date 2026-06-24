import streamlit as st
import sys
import os
from pathlib import Path

# ── Add backend to path ───────────────────────────────────────────
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "backend"))

# ── Direct imports from backend ───────────────────────────────────
try:
    from backend.rag_pipeline import ingest_pdf, query_document
    from backend.utils import (validate_pdf, generate_session_id,
                                get_upload_path, save_session_name,
                                load_session_registry)
except ImportError:
    from rag_pipeline import ingest_pdf, query_document
    from utils import (validate_pdf, generate_session_id,
                       get_upload_path, save_session_name,
                       load_session_registry)

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
.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d0d1a 50%, #0a0f1a 100%);
    color: #e0e0f0;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem; }
.hero-container { text-align: center; padding: 2.5rem 1rem 1.5rem; }
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(255,45,85,0.15), rgba(255,149,0,0.15));
    border: 1px solid rgba(255,45,85,0.4);
    border-radius: 20px; padding: 6px 18px;
    font-size: 0.75rem; font-weight: 600;
    color: #ff6b9d; letter-spacing: 0.1em;
    text-transform: uppercase; margin-bottom: 1rem;
}
.hero-title {
    font-size: 3.8rem; font-weight: 800;
    background: linear-gradient(135deg, #ff2d55 0%, #ff6b35 35%, #ff9500 60%, #ff2d55 100%);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradientShift 4s ease infinite;
    line-height: 1.1; margin: 0;
}
@keyframes gradientShift {
    0% { background-position: 0% center; }
    50% { background-position: 100% center; }
    100% { background-position: 0% center; }
}
.hero-subtitle { font-size: 1.1rem; color: #8888aa; margin: 0.8rem 0 0; }
.hero-subtitle span { color: #ff6b35; font-weight: 600; }
.glow-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #ff2d55, #ff6b35, #ff9500, transparent);
    border: none; margin: 1.5rem 0;
}
.feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1.5rem 0; }
.feature-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 1.2rem; text-align: center;
}
.feature-card-icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
.feature-card-title { font-size: 0.9rem; font-weight: 600; color: #e0e0f0; margin-bottom: 0.3rem; }
.feature-card-desc { font-size: 0.78rem; color: #6666aa; line-height: 1.5; }
.upload-zone {
    background: rgba(255,45,85,0.05);
    border: 2px dashed rgba(255,45,85,0.3);
    border-radius: 20px; padding: 2rem; text-align: center; margin: 1rem 0;
}
.upload-title { font-size: 1.1rem; font-weight: 600; color: #ff6b9d; margin-bottom: 0.3rem; }
.upload-sub { font-size: 0.8rem; color: #6666aa; }
.status-card {
    background: linear-gradient(135deg, rgba(255,45,85,0.1), rgba(255,149,0,0.1));
    border: 1px solid rgba(255,45,85,0.3);
    border-radius: 16px; padding: 1.2rem 1.5rem; margin: 1rem 0;
}
.status-title { font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: #ff9500; margin-bottom: 0.8rem; }
.status-row { display: flex; justify-content: space-between; align-items: center;
    margin: 0.4rem 0; font-size: 0.82rem; }
.status-label { color: #8888aa; }
.status-value { color: #ff6b9d; font-weight: 600; font-family: monospace; font-size: 0.8rem; }
.pulse-dot {
    display: inline-block; width: 8px; height: 8px; border-radius: 50%;
    background: #22c55e; margin-right: 6px;
    animation: pulse 2s ease infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}
.section-header {
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.12em; color: #ff2d55; margin: 1.5rem 0 0.7rem;
}
.metric-row { display: flex; gap: 0.6rem; flex-wrap: wrap; margin: 0.5rem 0; }
.metric-chip {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px; padding: 0.5rem 1rem;
    font-size: 0.8rem; color: #ccccee; text-align: center; flex: 1;
}
.metric-chip-value { font-size: 1.3rem; font-weight: 700; color: #ff6b35; display: block; }
.source-chip {
    display: inline-block;
    background: rgba(255,149,0,0.15);
    border: 1px solid rgba(255,149,0,0.4);
    border-radius: 6px; padding: 2px 10px;
    font-size: 0.72rem; color: #ff9500;
    margin: 0.4rem 0.2rem 0; font-weight: 500;
}
.stButton > button {
    background: linear-gradient(135deg, #ff2d55, #ff6b35) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(255,45,85,0.3) !important;
    width: 100% !important;
}
[data-testid="stSidebar"] {
    background: rgba(10,10,20,0.95) !important;
    border-right: 1px solid rgba(255,45,85,0.15) !important;
}
[data-testid="stSidebar"] * { color: #ccccee !important; }
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] div { color: #e0e0f0 !important; }
.stFileUploader {
    background: rgba(255,255,255,0.02) !important;
    border: 2px dashed rgba(255,45,85,0.3) !important;
    border-radius: 16px !important;
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

    # ── Session Manager ───────────────────────────────────────────
    st.markdown('<div class="section-header">🗂️ My Sessions</div>', unsafe_allow_html=True)
    try:
        sessions = load_session_registry()
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
                        st.rerun()
        else:
            st.markdown('<p style="font-size:0.75rem;color:#555577;">No sessions yet. Upload a PDF!</p>',
                       unsafe_allow_html=True)
    except Exception as e:
        st.markdown('<p style="font-size:0.75rem;color:#555577;">No sessions yet.</p>',
                   unsafe_allow_html=True)

    st.markdown("---")

    uploaded_file = st.file_uploader(
        label="Drop your PDF here",
        type=["pdf"],
        help="PDF files only | Max 10MB",
        label_visibility="collapsed"
    )
    st.markdown('<p style="font-size:0.75rem;color:#6666aa;text-align:center;margin-top:0.3rem;">PDF only · Max 10 MB</p>',
               unsafe_allow_html=True)

    if uploaded_file:
        if st.button("⚡ Process & Index Document"):
            with st.spinner("Indexing your document..."):
                try:
                    file_bytes = uploaded_file.getvalue()
                    is_valid, error_msg = validate_pdf(uploaded_file.name, len(file_bytes))
                    if not is_valid:
                        st.error(f"❌ {error_msg}")
                    else:
                        session_id = generate_session_id()
                        upload_path = get_upload_path(session_id, uploaded_file.name)

                        # Save file temporarily
                        with open(upload_path, "wb") as f:
                            f.write(file_bytes)

                        # Ingest into RAG pipeline
                        chunk_count = ingest_pdf(
                            pdf_path=str(upload_path),
                            session_id=session_id,
                            filename=uploaded_file.name
                        )

                        # Save session
                        save_session_name(session_id, uploaded_file.name, chunk_count)

                        st.session_state.session_id = session_id
                        st.session_state.filename = uploaded_file.name
                        st.session_state.chunk_count = chunk_count
                        st.session_state.chat_history = []
                        st.session_state.total_questions = 0
                        st.success(f"✅ Indexed {chunk_count} chunks!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    # Status card
    if st.session_state.session_id:
        fname_display = st.session_state.filename or ""
        fname_short = fname_display[:18] + "..." if len(fname_display) > 18 else fname_display
        st.markdown(f"""
        <div class="status-card">
            <div class="status-title">📄 Active Document</div>
            <div class="status-row">
                <span class="status-label">File</span>
                <span class="status-value">{fname_short}</span>
            </div>
            <div class="status-row">
                <span class="status-label">Chunks</span>
                <span class="status-value">{st.session_state.chunk_count}</span>
            </div>
            <div class="status-row">
                <span class="status-label">Session ID</span>
                <span class="status-value" style="color:#ff9500;">{st.session_state.session_id}</span>
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

    # System status
    st.markdown('<div class="section-header">🖥️ System</div>', unsafe_allow_html=True)
    st.markdown('<span class="pulse-dot"></span><span style="font-size:0.8rem;color:#22c55e;">Vaultiq Online</span>',
               unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.72rem;color:#555577;margin:4px 0;">Model: all-MiniLM-L6-v2</p>',
               unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.72rem;color:#555577;">LLM: Llama3 · Groq</p>',
               unsafe_allow_html=True)
    st.markdown('<div style="margin-top:2rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.06);font-size:0.7rem;color:#444466;text-align:center;">Vaultiq v1.0.0 · Built with ❤️</div>',
               unsafe_allow_html=True)

# ── Main area ─────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">🔐 RAG-Powered Document Intelligence</div>
    <h1 class="hero-title">VAULTIQ</h1>
    <p class="hero-subtitle">Ask anything about your documents — powered by <span>Llama3 × LangChain × FAISS</span></p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="glow-divider"/>', unsafe_allow_html=True)

if not st.session_state.session_id:
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-card-icon">🎯</div>
            <div class="feature-card-title">Zero Hallucination</div>
            <div class="feature-card-desc">Answers grounded strictly in your document context.</div>
        </div>
        <div class="feature-card">
            <div class="feature-card-icon">📑</div>
            <div class="feature-card-title">Source Citations</div>
            <div class="feature-card-desc">Every answer includes exact page references.</div>
        </div>
        <div class="feature-card">
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

    st.markdown(f'<div class="section-header">💬 Chat with {st.session_state.filename}</div>',
               unsafe_allow_html=True)

    # Chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["question"])
        with st.chat_message("assistant"):
            st.write(chat["answer"])
            if chat["sources"]:
                source_html = " ".join([f'<span class="source-chip">📄 {s}</span>' for s in chat["sources"]])
                st.markdown(source_html, unsafe_allow_html=True)

    # Input
    question = st.chat_input("Ask anything about your document...")

    if question and st.session_state.get("session_id"):
        with st.spinner("🔍 Searching through your document..."):
            try:
                result = query_document(
                    question=question,
                    session_id=st.session_state.session_id
                )
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": result["answer"],
                    "sources": result["sources"]
                })
                st.session_state.total_questions += 1
                st.rerun()
            except Exception as e:
                st.error(f"❌ {str(e)}")

    elif question and not st.session_state.get("session_id"):
        st.error("❌ Please upload a document first!")
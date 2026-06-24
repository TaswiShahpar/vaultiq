import os
import shutil
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

try:
    from models import QueryRequest, QueryResponse, UploadResponse, HealthResponse
    from rag_pipeline import ingest_pdf, query_document
    from utils import validate_pdf, generate_session_id, get_upload_path
except ImportError:
    from backend.models import QueryRequest, QueryResponse, UploadResponse, HealthResponse
    from backend.rag_pipeline import ingest_pdf, query_document
    from backend.utils import validate_pdf, generate_session_id, get_upload_path

# ── Lifespan (startup/shutdown) ───────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup and shutdown."""
    print("🔐 Vaultiq backend starting...")
    print("✅ RAG pipeline ready")
    yield
    print("🛑 Vaultiq backend shutting down...")


# ── FastAPI app ───────────────────────────────────────────────────
app = FastAPI(
    title="Vaultiq API",
    description="RAG-powered document intelligence backend",
    version="1.0.0",
    lifespan=lifespan
)

# ── CORS middleware ───────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if Vaultiq backend is running."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
@app.get("/sessions")
async def get_sessions():
    """Return all saved sessions."""
    from utils import load_session_registry
    registry = load_session_registry()
    return {"sessions": registry}


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file.
    Validates → saves → ingests into FAISS → returns session_id.
    """
    # Step 1 — Read file bytes to check size
    file_bytes = await file.read()
    file_size = len(file_bytes)

    # Step 2 — Validate file
    is_valid, error_msg = validate_pdf(file.filename, file_size)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Step 3 — Generate session ID
    session_id = generate_session_id()

    # Step 4 — Save PDF to uploads/
    upload_path = get_upload_path(session_id, file.filename)
    with open(upload_path, "wb") as f:
        f.write(file_bytes)

    # Step 5 — Ingest into RAG pipeline
    try:
        chunk_count = ingest_pdf(
            pdf_path=str(upload_path),
            session_id=session_id,
            filename=file.filename
        )
    except ValueError as e:
        # Clean up saved file if ingestion fails
        if upload_path.exists():
            upload_path.unlink()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        if upload_path.exists():
            upload_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(e)}"
        )
    # Save session to registry
    from utils import save_session_name
    save_session_name(session_id, file.filename, chunk_count)
    return UploadResponse(
        message="PDF uploaded and processed successfully.",
        filename=file.filename,
        chunk_count=chunk_count,
        session_id=session_id
    )


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    # If session_id is default, use latest available session
    session_id = request.session_id
    if session_id == "default" or not session_id:
        from utils import get_latest_session
        session_id = get_latest_session()
        if not session_id:
            raise HTTPException(status_code=404, detail="No document uploaded yet.")
    
    try:
        result = query_document(
            question=request.question,
            session_id=session_id
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )

    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"],
        session_id=request.session_id
    )
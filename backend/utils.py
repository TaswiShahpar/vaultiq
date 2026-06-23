import os
import uuid
from pathlib import Path
from typing import Optional

# ── Base directories ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
VECTORSTORE_DIR.mkdir(exist_ok=True)

# ── Constants ─────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


# ── File validation ───────────────────────────────────────────────
def validate_pdf(filename: str, file_size: int) -> tuple[bool, str]:
    """
    Validate uploaded file — checks extension and size.
    Returns (is_valid, error_message).
    """
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type '{ext}'. Only PDF files are allowed."

    if file_size > MAX_FILE_SIZE_BYTES:
        return False, f"File too large ({file_size / 1024 / 1024:.1f} MB). Maximum allowed size is {MAX_FILE_SIZE_MB} MB."

    return True, ""


# ── Session helpers ───────────────────────────────────────────────
def generate_session_id() -> str:
    """Generate a unique session ID for each upload."""
    return str(uuid.uuid4())[:8]


def get_upload_path(session_id: str, filename: str) -> Path:
    """Return the full path where uploaded PDF will be saved."""
    safe_filename = Path(filename).name  # strip any directory traversal
    return UPLOAD_DIR / f"{session_id}_{safe_filename}"


def get_vectorstore_path(session_id: str) -> str:
    """Return the FAISS vectorstore path for a given session."""
    session_dir = VECTORSTORE_DIR / session_id
    session_dir.mkdir(exist_ok=True)
    return str(session_dir)


# ── Cleanup helpers ───────────────────────────────────────────────
def cleanup_session_files(session_id: str, filename: str) -> None:
    """
    Delete uploaded PDF after processing.
    We keep vectorstore — needed for querying later.
    """
    upload_path = get_upload_path(session_id, filename)
    if upload_path.exists():
        upload_path.unlink()

def get_latest_session() -> Optional[str]:
    """Return the most recently created session ID."""
    if not VECTORSTORE_DIR.exists():
        return None
    sessions = [d for d in VECTORSTORE_DIR.iterdir() if d.is_dir()]
    if not sessions:
        return None
    latest = max(sessions, key=lambda d: d.stat().st_mtime)
    return latest.name

# Session registry file path
SESSION_REGISTRY = BASE_DIR / "session_registry.json"

def save_session_name(session_id: str, filename: str, chunk_count: int) -> None:
    """Save session with a human-readable name to registry."""
    import json
    from datetime import datetime
    
    registry = load_session_registry()
    registry[session_id] = {
        "filename": filename,
        "chunk_count": chunk_count,
        "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p")
    }
    with open(SESSION_REGISTRY, "w") as f:
        json.dump(registry, f, indent=2)


def load_session_registry() -> dict:
    """Load all saved sessions."""
    import json
    if not SESSION_REGISTRY.exists():
        return {}
    try:
        with open(SESSION_REGISTRY, "r") as f:
            return json.load(f)
    except:
        return {}


def delete_session(session_id: str) -> None:
    """Remove session from registry."""
    import json
    registry = load_session_registry()
    if session_id in registry:
        del registry[session_id]
        with open(SESSION_REGISTRY, "w") as f:
            json.dump(registry, f, indent=2)
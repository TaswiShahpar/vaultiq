# ── Base image ────────────────────────────────────────────────────
FROM python:3.11-slim

# ── Set working directory ─────────────────────────────────────────
WORKDIR /app

# ── Install system dependencies ───────────────────────────────────
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Copy requirements first (layer caching) ───────────────────────
COPY requirements.txt .

# ── Install Python dependencies ───────────────────────────────────
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project files ────────────────────────────────────────────
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# ── Create necessary directories ──────────────────────────────────
RUN mkdir -p vectorstore uploads

# ── Expose ports ──────────────────────────────────────────────────
EXPOSE 8000 8501

# ── Startup script ───────────────────────────────────────────────
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
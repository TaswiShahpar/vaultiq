---
title: Vaultiq
emoji: 🔐
colorFrom: red
colorTo: yellow
sdk: docker
pinned: true
app_port: 8501
---
# 🔐 Vaultiq — RAG-Powered Document Intelligence

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat&logo=python)
![LangChain](https://img.shields.io/badge/LangChain-0.3.14-green?style=flat)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)
![FAISS](https://img.shields.io/badge/FAISS-Vector_DB-orange?style=flat)
![Groq](https://img.shields.io/badge/Groq-Llama3-purple?style=flat)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39-red?style=flat&logo=streamlit)

> Ask anything about your documents — grounded answers, zero hallucination, with source citations.

---

## 🎯 What is Vaultiq?

Vaultiq is a production-ready **Retrieval-Augmented Generation (RAG)** application that lets you upload any PDF and ask questions about it. Unlike ChatGPT, Vaultiq answers **strictly from your document** — no hallucinations, every answer cited with page numbers.

**Built for:** Legal firms, HR teams, researchers, students, financial analysts.

---

## 🏗️ Architecture
```text
PDF Upload

↓

PyPDF Loader → Text Extraction

↓

RecursiveCharacterTextSplitter → 500-word chunks (50 overlap)

↓

HuggingFace sentence-transformers → Embeddings (all-MiniLM-L6-v2)

↓

FAISS Vector Store → Saved to disk (session-based)

↓

User Query → Embedded → Similarity Search (top-4 chunks)

↓

Groq Llama3 → Context-grounded Answer + Page Citations

↓

FastAPI → Streamlit UI
```
---

## ✨ Features

- 📄 **PDF Intelligence** — Upload any PDF, ask anything
- 🎯 **Zero Hallucination** — Answers grounded strictly in document context
- 📑 **Source Citations** — Every answer includes exact page references
- ⚡ **Groq Speed** — Ultra-fast Llama3-8b inference
- 🗂️ **Session Manager** — Save and reload document sessions anytime
- 🔐 **Privacy First** — PDFs deleted after processing, only vectors stored
- 🌐 **REST API** — Full FastAPI backend with Swagger documentation

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Groq — Llama3-8b-instant |
| Embeddings | HuggingFace — all-MiniLM-L6-v2 |
| Vector DB | FAISS (Facebook AI Similarity Search) |
| RAG Framework | LangChain 0.3.14 |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| PDF Processing | PyPDF |
| Validation | Pydantic v2 |

---

## 🚀 Run Locally

### Prerequisites
- Python 3.10+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Setup

```bash
# Clone the repo
git clone https://github.com/TaswiShahpar/vaultiq.git
cd vaultiq

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env
```

### Run

```bash
# Terminal 1 — Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
streamlit run frontend/app.py
```

Open `http://localhost:8501` in your browser.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Backend health check |
| POST | `/upload` | Upload and index PDF |
| POST | `/query` | Ask question about document |
| GET | `/sessions` | List all saved sessions |

Full interactive API docs at `http://localhost:8000/docs`

---

## 📁 Project Structure
```text
vaultiq/

├── backend/

│   ├── main.py          # FastAPI app — endpoints

│   ├── rag_pipeline.py  # LangChain RAG logic

│   ├── models.py        # Pydantic schemas

│   └── utils.py         # Helper functions

├── frontend/

│   └── app.py           # Streamlit UI

├── vectorstore/         # FAISS indexes (git-ignored)

├── uploads/             # Temp PDF storage (git-ignored)

├── requirements.txt

└── .env                 # API keys (git-ignored)
```
---

## 🔮 Roadmap

- [ ] Multi-document support (query across multiple PDFs)
- [ ] Hybrid retrieval (semantic + keyword BM25)
- [ ] Chat memory (multi-turn conversations)
- [ ] HuggingFace Spaces deployment
- [ ] User authentication

---

## 👩‍💻 Author

**Taswi Shahpar** — [LinkedIn](https://linkedin.com/in/taswi-shahpar-900070237) · [GitHub](https://github.com/TaswiShahpar) · [Kaggle](https://kaggle.com/taswishahpar)

---

*Built with ❤️ using LangChain, FAISS, FastAPI, and Groq*
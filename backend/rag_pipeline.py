import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

try:
    from utils import get_vectorstore_path, cleanup_session_files
except ImportError:
    from backend.utils import get_vectorstore_path, cleanup_session_files

# ── Load environment variables ────────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Please set it as environment variable.")

# ── Embedding model (runs locally, no API needed) ─────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ── LLM config ───────────────────────────────────────────────────
LLM_MODEL = "llama-3.1-8b-instant"
MAX_TOKENS = 1024
TEMPERATURE = 0.2  # low = more factual, less creative

# ── Chunking config ───────────────────────────────────────────────
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# ── Prompt template ───────────────────────────────────────────────
PROMPT_TEMPLATE = """
You are Vaultiq, an intelligent document assistant.
Answer the question based ONLY on the context provided below.
If the answer is not found in the context, say:
"I couldn't find this information in the uploaded document."
Do NOT make up answers.

Context:
{context}

Question:
{question}

Answer:
"""


def get_embeddings():
    """Load HuggingFace embedding model (cached after first load)."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


def get_llm():
    """Initialize Groq LLM."""
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=LLM_MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )


def ingest_pdf(pdf_path: str, session_id: str, filename: str) -> int:
    """
    Load PDF → split into chunks → embed → save to FAISS.
    Returns number of chunks created.
    """
    # Step 1 — Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    if not documents:
        raise ValueError("Could not extract text from PDF. File may be scanned or empty.")

    # Step 2 — Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("PDF has no extractable text content.")

    # Step 3 — Embed and store in FAISS
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # Step 4 — Save vectorstore to disk
    vectorstore_path = get_vectorstore_path(session_id)
    vectorstore.save_local(str(Path(vectorstore_path).resolve()).replace("\\", "/"))

    # Step 5 — Delete PDF after processing (privacy)
    cleanup_session_files(session_id, filename)

    return len(chunks)


def query_document(question: str, session_id: str) -> dict:
    """
    Load FAISS vectorstore → retrieve relevant chunks → ask LLM.
    Returns answer and source page numbers.
    """
    vectorstore_path = get_vectorstore_path(session_id)

    # Check vectorstore exists
    vs_path = Path(vectorstore_path)
    index_file = vs_path / "index.faiss"
    
    if not vs_path.exists() or not index_file.exists():
        raise FileNotFoundError(
            "No document found for this session. Please upload a PDF first."
        )

    # Step 1 — Load vectorstore
    embeddings = get_embeddings()
    vectorstore = FAISS.load_local(
    folder_path=str(Path(vectorstore_path).resolve()).replace("\\", "/"),
    embeddings=embeddings,
    allow_dangerous_deserialization=True
    )
    # Step 2 — Build retriever (top 4 most relevant chunks)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    # Step 3 — Build prompt
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )

    # Step 4 — Build RAG chain
    llm = get_llm()
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    # Step 5 — Run query
    result = rag_chain.invoke({"query": question})

    # Step 6 — Extract source page numbers
    sources = []
    for doc in result.get("source_documents", []):
        page = doc.metadata.get("page", None)
        if page is not None:
            sources.append(f"Page {page + 1}")

    # Deduplicate sources
    sources = list(dict.fromkeys(sources))

    return {
        "answer": result["result"],
        "sources": sources
    }
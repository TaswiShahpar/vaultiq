from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    """Schema for incoming question from user."""
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="The question to ask about the uploaded document"
    )
    session_id: Optional[str] = Field(
        default="default",
        description="Session identifier to support multiple users"
    )


class QueryResponse(BaseModel):
    """Schema for answer returned to user."""
    answer: str = Field(description="LLM generated answer from document context")
    sources: list[str] = Field(
        default=[],
        description="Page numbers or chunks used to generate the answer"
    )
    session_id: str = Field(description="Echo back the session id")


class UploadResponse(BaseModel):
    """Schema for PDF upload confirmation."""
    message: str
    filename: str
    chunk_count: int = Field(description="Number of chunks created from the PDF")
    session_id: str


class HealthResponse(BaseModel):
    """Schema for health check endpoint."""
    status: str
    version: str = "1.0.0"
    model: str = "sentence-transformers/all-MiniLM-L6-v2"
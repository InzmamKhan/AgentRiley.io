from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    query: str = Field(..., description="Tactical briefing or intel query for Agent Riley")
    top_k: Optional[int] = Field(default=4, description="Number of context chunks to retrieve")

class DocumentSource(BaseModel):
    source: str
    chunk_id: int
    content: str
    score: float

class QueryResponse(BaseModel):
    callsign: str = "Agent Riley [Bravo 0-7]"
    status: str
    answer: str
    sources: List[DocumentSource] = []

class IndexStatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    document_files: List[str]
    vector_dim: int
    indexed_at: Optional[str] = None

class IngestResponse(BaseModel):
    status: str
    message: str
    indexed_files: List[str]
    total_chunks: int

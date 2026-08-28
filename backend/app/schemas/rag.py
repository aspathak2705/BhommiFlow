from pydantic import BaseModel
from typing import List, Optional

class KnowledgeSourceResponse(BaseModel):
    source_id: str
    title: str
    department: str
    source_url: Optional[str] = None
    scope: str

    class Config:
        from_attributes = True

class ChunkReferenceResponse(BaseModel):
    chunk_id: str
    source_id: str
    section: Optional[str] = None
    page_number: Optional[str] = None

    class Config:
        from_attributes = True

class RAGQueryRequest(BaseModel):
    question: str

class RAGQueryResponse(BaseModel):
    answer: str
    sources: List[KnowledgeSourceResponse] = []
    retrieved_chunks: List[ChunkReferenceResponse] = []

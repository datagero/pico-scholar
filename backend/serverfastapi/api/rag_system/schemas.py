from pydantic import BaseModel
from typing import List, Dict, Optional

# Base schema for the query
class RAGQueryBase(BaseModel):
    initial_query: str

class RAGQueryCreate(RAGQueryBase):
    pass

class RAGQuery(RAGQueryBase):
    id: int
    expanded_queries: Optional[List[str]] = []
    
    class Config:
        orm_mode = True

# Summarization schemas
class SummarizeRequest(BaseModel):
    document_ids: List[int]

class SummarizeResponse(BaseModel):
    summary: str  # Single summary combining all provided document contents

# Chat schemas
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    response: str

# Query expansion schema
class QueryExpansionRequest(BaseModel):
    initial_query: str

class QueryExpansionResponse(BaseModel):
    alternatives: List[str]

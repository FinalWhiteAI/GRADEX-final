# schemas.py
from pydantic import BaseModel
from typing import List, Dict, Any

class QueryRequest(BaseModel):
    user_id: str
    document_id: str 
    query: str

class UploadResponse(BaseModel):
    message: str
    chunks_stored: int
    file_name: str
    user_id: str
    document_id: str

class QueryResponse(BaseModel):
    """For returning just the context chunks"""
    context: List[Dict[str, Any]]

class RAGQueryRequest(BaseModel):
    """New schema for the conversational RAG endpoint"""
    user_id: str
    document_id: str
    query: str
    chat_session_id: str 

class RAGQueryResponse(BaseModel):
    """For returning the final LLM answer"""
    answer: str
    context: List[Dict[str, Any]]


class DocumentInfo(BaseModel):
    """Represents a single uploaded document's metadata."""
    document_id: str
    file_name: str
    
class DocumentListResponse(BaseModel):
    """The response model for the list of documents."""
    documents: List[DocumentInfo]
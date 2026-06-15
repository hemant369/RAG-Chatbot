from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class DocumentMetadata(BaseModel):
    doc_id: str
    filename: str
    file_hash: str
    indexed_at: Optional[datetime] = None
    chunk_count: int

class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]

class DocumentUploadResponse(BaseModel):
    success: bool
    doc_id: str
    filename: str
    message: str

class DocumentDeleteRequest(BaseModel):
    doc_id: str

class DocumentDeleteResponse(BaseModel):
    success: bool
    message: str
from pydantic import BaseModel
from typing import List

class DocumentMetadata(BaseModel):
    doc_id: str
    filename: str
    file_hash: str
    chunk_count: int

class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]

class DocumentUploadResponse(BaseModel):
    success: bool
    doc_id: str
    filename: str
    message: str
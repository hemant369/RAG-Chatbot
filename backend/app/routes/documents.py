from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import aiofiles

from app.schemas.documents import (
    DocumentListResponse, DocumentMetadata, DocumentUploadResponse
)
from app.utils.document_manager import DocumentManager
from app.utils.logger import setup_logger

router = APIRouter(prefix="/documents", tags=["documents"])
logger = setup_logger(__name__)
doc_manager = DocumentManager()

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document for indexing.
    Supported formats: PDF, TXT, MD, CSV, JSON, YAML
    """
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Index document
        doc_id = doc_manager.index_document(str(file_path))
        
        logger.info(f"Document indexed: {file.filename} -> {doc_id}")
        
        return DocumentUploadResponse(
            success=True,
            doc_id=doc_id,
            filename=file.filename,
            message=f"Document '{file.filename}' successfully indexed"
        )
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

@router.get("/list", response_model=DocumentListResponse)
async def list_documents():
    """Get list of indexed documents with metadata."""
    try:
        docs = doc_manager.list_documents()
        
        document_list = [
            DocumentMetadata(
                doc_id=doc.get("id", ""),
                filename=doc.get("filename", ""),
                file_hash=doc.get("hash", ""),
                chunk_count=doc.get("chunks", 0)
            )
            for doc in docs
        ]
        
        return DocumentListResponse(documents=document_list)
    
    except Exception as e:
        logger.error(f"List error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.get("/{doc_id}")
async def get_document(doc_id: str):
    """Get metadata for a specific document."""
    try:
        doc = doc_manager.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentMetadata(
            doc_id=doc.get("id", ""),
            filename=doc.get("filename", ""),
            file_hash=doc.get("hash", ""),
            chunk_count=doc.get("chunks", 0)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document from the index."""
    try:
        success = doc_manager.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        logger.info(f"Document deleted: {doc_id}")
        
        return {"success": True, "message": f"Document {doc_id} deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
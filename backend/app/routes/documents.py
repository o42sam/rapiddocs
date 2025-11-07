from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from app.database import get_database
from app.schemas.request import DocumentResponse

router = APIRouter()


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents():
    """List all generated documents"""
    db = get_database()

    documents = await db.documents.find().sort("created_at", -1).limit(50).to_list(50)

    return [
        DocumentResponse(
            id=str(doc["_id"]),
            title=doc.get("title", "Untitled"),
            description=doc.get("description", ""),
            status=doc.get("status", "pending"),
            created_at=doc.get("created_at").isoformat(),
            updated_at=doc.get("updated_at").isoformat(),
            completed_at=doc.get("completed_at").isoformat() if doc.get("completed_at") else None,
            pdf_url=doc.get("files", {}).get("pdf_url")
        )
        for doc in documents
    ]


@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str):
    """Get document by ID"""
    db = get_database()

    try:
        doc = await db.documents.find_one({"_id": ObjectId(doc_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid document ID")

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(
        id=str(doc["_id"]),
        title=doc.get("title", "Untitled"),
        description=doc.get("description", ""),
        status=doc.get("status", "pending"),
        created_at=doc.get("created_at").isoformat(),
        updated_at=doc.get("updated_at").isoformat(),
        completed_at=doc.get("completed_at").isoformat() if doc.get("completed_at") else None,
        pdf_url=doc.get("files", {}).get("pdf_url")
    )


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete document"""
    db = get_database()

    try:
        result = await db.documents.delete_one({"_id": ObjectId(doc_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid document ID")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"message": "Document deleted successfully"}

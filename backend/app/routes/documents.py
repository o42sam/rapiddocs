from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from app.database import get_database
from app.schemas.request import DocumentResponse
from app.models.user import User
from app.utils.dependencies import get_current_active_user

router = APIRouter()


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(current_user: User = Depends(get_current_active_user)):
    """List all generated documents for the authenticated user"""
    db = get_database()

    # Filter documents by user_id
    documents = await db.documents.find(
        {"user_id": str(current_user.id)}
    ).sort("created_at", -1).limit(50).to_list(50)

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
async def get_document(doc_id: str, current_user: User = Depends(get_current_active_user)):
    """Get document by ID (only if owned by current user)"""
    db = get_database()

    try:
        doc = await db.documents.find_one({
            "_id": ObjectId(doc_id),
            "user_id": str(current_user.id)
        })
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
async def delete_document(doc_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete document (only if owned by current user)"""
    db = get_database()

    try:
        result = await db.documents.delete_one({
            "_id": ObjectId(doc_id),
            "user_id": str(current_user.id)
        })
    except:
        raise HTTPException(status_code=400, detail="Invalid document ID")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"message": "Document deleted successfully"}

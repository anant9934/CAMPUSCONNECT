import os
import shutil
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import KnowledgeDocument, KnowledgeChunk, Category, AdminUser, AuditLog
from app.api.v1.endpoints.admin_auth import get_current_admin
from app.schemas.document import DocumentOut, ChunkOut
from app.services.document_service import process_document_file, DocumentProcessingError
from app.services.rag.hybrid_search import hybrid_search_engine

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/admin/documents", response_model=List[DocumentOut])
async def list_documents(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """List uploaded knowledge base documents."""
    stmt = (
        select(KnowledgeDocument)
        .options(selectinload(KnowledgeDocument.category))
        .order_by(KnowledgeDocument.created_at.desc())
    )
    res = await db.execute(stmt)
    docs = res.scalars().all()

    out = []
    for d in docs:
        out.append(
            DocumentOut(
                id=str(d.id),
                category_id=str(d.category_id) if d.category_id else None,
                category_name=d.category.name if d.category else None,
                title=d.title,
                filename=d.filename,
                file_size=d.file_size,
                mime_type=d.mime_type,
                status=d.status,
                is_approved=d.is_approved,
                total_chunks=d.total_chunks,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
        )
    return out


@router.post("/admin/documents", response_model=DocumentOut)
async def upload_document(
    title: str = Form(...),
    category_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and ingest an institutional document (PDF, DOCX, TXT).
    Validates, extracts text, cleans, chunks, and queues for administrative review.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload PDF, DOCX, or TXT."
        )

    saved_filename = f"{uuid.uuid4().hex}_{file.filename}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(saved_path)

    # Process chunks
    try:
        chunks_data = process_document_file(saved_path, file.content_type or "text/plain")
    except DocumentProcessingError as e:
        os.remove(saved_path)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    doc = KnowledgeDocument(
        category_id=category_id,
        title=title,
        filename=file.filename,
        file_path=saved_path,
        file_size=file_size,
        mime_type=file.content_type or "text/plain",
        status="pending",
        is_approved=False,
        total_chunks=len(chunks_data),
        uploaded_by_id=admin.id,
    )
    db.add(doc)
    await db.flush()

    for item in chunks_data:
        chunk = KnowledgeChunk(
            document_id=doc.id,
            chunk_index=item["chunk_index"],
            content=item["content"],
            clean_text=item["clean_text"],
            page_number=item.get("page_number"),
            token_count=item.get("token_count", 0),
        )
        db.add(chunk)

    audit = AuditLog(
        admin_id=admin.id,
        action="upload_document",
        resource_type="document",
        resource_id=str(doc.id),
        details={"title": title, "filename": file.filename, "chunks": len(chunks_data)},
    )
    db.add(audit)
    await db.commit()
    await db.refresh(doc)

    cat_name = None
    if doc.category_id:
        c_res = await db.execute(select(Category).where(Category.id == doc.category_id))
        cat = c_res.scalars().first()
        if cat:
            cat_name = cat.name

    return DocumentOut(
        id=str(doc.id),
        category_id=str(doc.category_id) if doc.category_id else None,
        category_name=cat_name,
        title=doc.title,
        filename=doc.filename,
        file_size=doc.file_size,
        mime_type=doc.mime_type,
        status=doc.status,
        is_approved=doc.is_approved,
        total_chunks=doc.total_chunks,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.get("/admin/documents/{id}/chunks", response_model=List[ChunkOut])
async def get_document_chunks(
    id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Inspect extracted chunks of a document for administrative verification."""
    stmt = (
        select(KnowledgeChunk)
        .where(KnowledgeChunk.document_id == id)
        .order_by(KnowledgeChunk.chunk_index.asc())
    )
    res = await db.execute(stmt)
    chunks = res.scalars().all()
    return [
        ChunkOut(
            id=str(c.id),
            chunk_index=c.chunk_index,
            content=c.content,
            page_number=c.page_number,
            token_count=c.token_count,
        )
        for c in chunks
    ]


@router.post("/admin/documents/{id}/approve")
async def approve_document(
    id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Approve document for student RAG indexing."""
    stmt = select(KnowledgeDocument).where(KnowledgeDocument.id == id)
    res = await db.execute(stmt)
    doc = res.scalars().first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    doc.status = "approved"
    doc.is_approved = True

    audit = AuditLog(
        admin_id=admin.id,
        action="approve_document",
        resource_type="document",
        resource_id=str(doc.id),
        details={"title": doc.title},
    )
    db.add(audit)
    await db.commit()

    # Rebuild search index to include approved chunks
    await hybrid_search_engine.build_index(db)

    return {"status": "success", "message": f"Document '{doc.title}' approved and indexed."}


@router.delete("/admin/documents/{id}")
async def delete_document(
    id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document and its chunks."""
    stmt = select(KnowledgeDocument).where(KnowledgeDocument.id == id)
    res = await db.execute(stmt)
    doc = res.scalars().first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    audit = AuditLog(
        admin_id=admin.id,
        action="delete_document",
        resource_type="document",
        resource_id=str(doc.id),
        details={"title": doc.title},
    )
    db.add(audit)
    await db.delete(doc)
    await db.commit()

    # Rebuild index
    await hybrid_search_engine.build_index(db)
    return {"status": "success", "message": "Document removed."}


"""Document upload, list, delete endpoints."""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.config import settings
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import Document, User
from backend.schemas import DocumentOut, MessageResponse

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_TYPES = {"application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}
MAX_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(Document.user_id == current_user.id).order_by(Document.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=DocumentOut, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not supported. Use PDF, TXT, or DOCX.")

    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.MAX_FILE_SIZE_MB} MB limit.")

    # Save to disk
    safe_name = f"{uuid.uuid4()}{ext}"
    dest = Path(settings.UPLOAD_DIR) / current_user.id
    dest.mkdir(parents=True, exist_ok=True)
    file_path = dest / safe_name
    file_path.write_bytes(content)

    doc = Document(
        user_id=current_user.id,
        filename=str(file_path),
        original_name=file.filename,
        file_type=ext.lstrip("."),
        file_size=len(content),
        status="pending",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Kick off processing in background (Phase 5 will implement this)
    background_tasks.add_task(_process_document_placeholder, doc.id)

    return DocumentOut.model_validate(doc)


async def _process_document_placeholder(doc_id: str):
    """Placeholder – real processing added in Phase 5."""
    pass


@router.delete("/{doc_id}", response_model=MessageResponse)
async def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc: Document | None = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if doc.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied.")

    # Remove file from disk
    try:
        if os.path.exists(doc.filename):
            os.remove(doc.filename)
    except OSError:
        pass

    await db.delete(doc)
    await db.commit()
    return {"message": "Document deleted."}


@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc: Document | None = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if doc.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied.")
    return DocumentOut.model_validate(doc)

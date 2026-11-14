"""Admin panel endpoints – all require admin role."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.database import get_db
from backend.dependencies import require_admin
from backend.models import User, Document, Conversation, Message, ActivityLog
from backend.schemas import (
    AdminStatsResponse, AdminUserStatusRequest,
    UserPublic, ActivityLogOut, MessageResponse,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStatsResponse)
async def get_stats(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar()
    active_users = (await db.execute(select(func.count()).select_from(User).where(User.is_active == True))).scalar()
    total_docs = (await db.execute(select(func.count()).select_from(Document))).scalar()
    indexed_docs = (await db.execute(select(func.count()).select_from(Document).where(Document.status == "indexed"))).scalar()
    total_convs = (await db.execute(select(func.count()).select_from(Conversation))).scalar()
    total_msgs = (await db.execute(select(func.count()).select_from(Message))).scalar()

    return AdminStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_documents=total_docs,
        indexed_documents=indexed_docs,
        total_conversations=total_convs,
        total_messages=total_msgs,
    )


@router.get("/users", response_model=list[UserPublic])
async def list_users(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.patch("/users/{user_id}/status", response_model=UserPublic)
async def set_user_status(
    user_id: str,
    body: AdminUserStatusRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user: User | None = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account.")
    user.is_active = body.is_active
    await db.commit()
    await db.refresh(user)
    return UserPublic.model_validate(user)


@router.get("/documents", response_model=list[dict])
async def list_all_documents(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document, User.name, User.email)
        .join(User, User.id == Document.user_id)
        .order_by(Document.created_at.desc())
    )
    rows = result.all()
    out = []
    for doc, uname, uemail in rows:
        out.append({
            "id": doc.id,
            "original_name": doc.original_name,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "status": doc.status,
            "created_at": doc.created_at.isoformat(),
            "owner_name": uname,
            "owner_email": uemail,
        })
    return out


@router.get("/logs", response_model=list[ActivityLogOut])
async def get_logs(
    limit: int = 100,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit)
    )
    return result.scalars().all()

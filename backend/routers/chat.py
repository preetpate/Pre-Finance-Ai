"""Chat / conversation endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import Conversation, Message, User
from backend.schemas import (
    AskRequest, AskResponse, ConversationOut, ConversationDetail,
    RenameConversationRequest, MessageResponse,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/conversations", response_model=list[ConversationOut])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    return result.scalars().all()


@router.get("/conversations/{conv_id}", response_model=ConversationDetail)
async def get_conversation(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv: Conversation | None = result.scalar_one_or_none()
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    msgs = await db.execute(
        select(Message).where(Message.conversation_id == conv_id).order_by(Message.created_at)
    )
    conv.messages = msgs.scalars().all()
    return conv


@router.patch("/conversations/{conv_id}/rename", response_model=ConversationOut)
async def rename_conversation(
    conv_id: str,
    body: RenameConversationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv: Conversation | None = result.scalar_one_or_none()
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    conv.title = body.title.strip() or "Untitled"
    await db.commit()
    await db.refresh(conv)
    return conv


@router.delete("/conversations/{conv_id}", response_model=MessageResponse)
async def delete_conversation(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv: Conversation | None = result.scalar_one_or_none()
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    await db.delete(conv)
    await db.commit()
    return {"message": "Conversation deleted."}


@router.post("/ask", response_model=AskResponse)
async def ask(
    body: AskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get or create conversation
    if body.conversation_id:
        result = await db.execute(select(Conversation).where(Conversation.id == body.conversation_id))
        conv: Conversation | None = result.scalar_one_or_none()
        if not conv or conv.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Conversation not found.")
    else:
        conv = Conversation(user_id=current_user.id, title=body.question[:60])
        db.add(conv)
        await db.flush()

    # Save user message
    user_msg = Message(conversation_id=conv.id, role="user", content=body.question)
    db.add(user_msg)
    await db.flush()

    # ── RAG pipeline (Phase 6 will replace this stub) ──────────────────────
    answer = (
        "AI processing is not yet configured. "
        "Please complete Phase 5 (document processing) and Phase 6 (RAG) setup first."
    )
    sources = []
    # ───────────────────────────────────────────────────────────────────────

    ai_msg = Message(conversation_id=conv.id, role="assistant", content=answer)
    db.add(ai_msg)
    await db.commit()
    await db.refresh(ai_msg)
    await db.refresh(conv)

    return AskResponse(
        conversation_id=conv.id,
        answer=answer,
        sources=sources,
        message_id=ai_msg.id,
    )

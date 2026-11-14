"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
import re


# ─── Auth ─────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain an uppercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain a digit.")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty.")
        return v.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain an uppercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain a digit.")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserPublic"


# ─── Users ────────────────────────────────────────────────────────────────────

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    role: str
    is_active: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class AdminUserStatusRequest(BaseModel):
    is_active: bool


# ─── Documents ────────────────────────────────────────────────────────────────

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    original_name: str
    file_type: str
    file_size: int
    page_count: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ─── Chat ─────────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    conversation_id: Optional[str] = None
    question: str

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Question cannot be empty.")
        return v.strip()


class CitationOut(BaseModel):
    document_name: str
    page_number: Optional[int] = None
    chunk_index: int
    snippet: str


class AskResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: List[CitationOut]
    message_id: str


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    content: str
    sources: Optional[str] = None  # raw JSON
    created_at: datetime


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationDetail(ConversationOut):
    messages: List[MessageOut] = []


class RenameConversationRequest(BaseModel):
    title: str


# ─── Admin ────────────────────────────────────────────────────────────────────

class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_documents: int
    indexed_documents: int
    total_conversations: int
    total_messages: int


class ActivityLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str] = None
    action: str
    detail: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime


# ─── Generic ──────────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str

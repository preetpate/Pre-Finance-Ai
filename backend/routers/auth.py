"""Authentication endpoints: register, login, logout, me, change-password."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import User, ActivityLog
from backend.schemas import (
    RegisterRequest, LoginRequest, TokenResponse,
    ChangePasswordRequest, UserPublic, MessageResponse,
)
from backend.security.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _log(db: AsyncSession, user_id: str | None, action: str, detail: str = "", ip: str = ""):
    log = ActivityLog(user_id=user_id, action=action, detail=detail, ip_address=ip)
    db.add(log)


@router.post("/register", response_model=MessageResponse, status_code=201)
async def register(body: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email.lower()))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered.")

    user = User(
        name=body.name,
        email=body.email.lower(),
        hashed_password=hash_password(body.password),
        role="user",
    )
    db.add(user)
    await db.flush()
    _log(db, user.id, "REGISTER", f"New user: {user.email}", request.client.host if request.client else "")
    await db.commit()
    return {"message": "Account created. Please log in."}


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email.lower()))
    user: User | None = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated. Contact admin.")

    user.last_login = datetime.now(timezone.utc)
    _log(db, user.id, "LOGIN", ip=request.client.host if request.client else "")
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(access_token=token, user=UserPublic.model_validate(user))


@router.post("/logout", response_model=MessageResponse)
async def logout(request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # JWT is stateless; client must discard the token.
    # We log the action server-side for audit.
    _log(db, current_user.id, "LOGOUT", ip=request.client.host if request.client else "")
    await db.commit()
    return {"message": "Logged out successfully."}


@router.get("/me", response_model=UserPublic)
async def me(current_user: User = Depends(get_current_user)):
    return UserPublic.model_validate(current_user)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    current_user.hashed_password = hash_password(body.new_password)
    _log(db, current_user.id, "CHANGE_PASSWORD")
    await db.commit()
    return {"message": "Password updated successfully."}

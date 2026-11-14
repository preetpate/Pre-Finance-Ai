"""User profile endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import User
from backend.schemas import UserPublic, UserUpdateRequest, MessageResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserPublic)
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserPublic.model_validate(current_user)


@router.patch("/me", response_model=UserPublic)
async def update_profile(
    body: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.name is not None:
        if not body.name.strip():
            raise HTTPException(status_code=400, detail="Name cannot be empty.")
        current_user.name = body.name.strip()
    if body.avatar_url is not None:
        current_user.avatar_url = body.avatar_url
    await db.commit()
    await db.refresh(current_user)
    return UserPublic.model_validate(current_user)

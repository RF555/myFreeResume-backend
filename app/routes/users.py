from fastapi import APIRouter, Depends

from app.database import get_db
from app.dependencies import get_current_user
from app.models.entry import ResumeData
from app.models.user import UserResponse, UserUpdate, ResumeProfileResponse
from app.services.user_service import update_user

router = APIRouter(prefix="/api/users", tags=["users"])


def _has_profile(user: dict) -> bool:
    profile = user.get("resume_profile", {})
    return bool(profile.get("name"))


def _user_response(user: dict) -> UserResponse:
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user["name"],
        oauth_providers=user.get("oauth_providers", []),
        has_resume_profile=_has_profile(user),
        created_at=user["created_at"],
        updated_at=user["updated_at"],
    )


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    return _user_response(current_user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    updates = data.model_dump(exclude_none=True)
    if not updates:
        return _user_response(current_user)

    updated = await update_user(db, str(current_user["_id"]), updates)
    return _user_response(updated)


@router.get("/me/resume-profile", response_model=ResumeProfileResponse)
async def get_resume_profile(current_user: dict = Depends(get_current_user)):
    profile = current_user.get("resume_profile", ResumeData().model_dump())
    return ResumeProfileResponse(resume_profile=profile)


@router.put("/me/resume-profile", response_model=ResumeProfileResponse)
async def update_resume_profile(
    data: ResumeData,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    updated = await update_user(
        db,
        str(current_user["_id"]),
        {"resume_profile": data.model_dump()},
    )
    return ResumeProfileResponse(resume_profile=updated["resume_profile"])

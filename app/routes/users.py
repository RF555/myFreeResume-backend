from fastapi import APIRouter, Depends

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import UserResponse, UserUpdate
from app.services.user_service import update_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        name=current_user["name"],
        oauth_providers=current_user.get("oauth_providers", []),
        created_at=current_user["created_at"],
        updated_at=current_user["updated_at"],
    )


@router.put("/me", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    updates = data.model_dump(exclude_none=True)
    if not updates:
        return UserResponse(
            id=str(current_user["_id"]),
            email=current_user["email"],
            name=current_user["name"],
            oauth_providers=current_user.get("oauth_providers", []),
            created_at=current_user["created_at"],
            updated_at=current_user["updated_at"],
        )

    updated = await update_user(db, str(current_user["_id"]), updates)
    return UserResponse(
        id=str(updated["_id"]),
        email=updated["email"],
        name=updated["name"],
        oauth_providers=updated.get("oauth_providers", []),
        created_at=updated["created_at"],
        updated_at=updated["updated_at"],
    )

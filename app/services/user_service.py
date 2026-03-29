from datetime import datetime, timezone

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.exceptions import ConflictError, NotFoundError


async def create_user(
    db: AsyncDatabase,
    email: str,
    name: str,
    password_hash: str | None = None,
    oauth_providers: list | None = None,
) -> dict:
    existing = await db.users.find_one({"email": email})
    if existing:
        raise ConflictError("Email already registered")

    now = datetime.now(timezone.utc)
    user_doc = {
        "email": email,
        "password_hash": password_hash,
        "name": name,
        "oauth_providers": oauth_providers or [],
        "created_at": now,
        "updated_at": now,
    }
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return user_doc


async def get_user_by_email(db: AsyncDatabase, email: str) -> dict | None:
    return await db.users.find_one({"email": email})


async def get_user_by_id(db: AsyncDatabase, user_id: str) -> dict | None:
    return await db.users.find_one({"_id": ObjectId(user_id)})


async def update_user(db: AsyncDatabase, user_id: str, updates: dict) -> dict:
    updates["updated_at"] = datetime.now(timezone.utc)
    result = await db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": updates},
        return_document=True,
    )
    if not result:
        raise NotFoundError("User not found")
    return result


async def find_or_create_oauth_user(
    db: AsyncDatabase,
    email: str,
    name: str,
    provider: str,
    provider_id: str,
) -> dict:
    user = await db.users.find_one({"email": email})
    if user:
        providers = user.get("oauth_providers", [])
        if not any(
            p["provider"] == provider and p["provider_id"] == provider_id
            for p in providers
        ):
            providers.append({"provider": provider, "provider_id": provider_id})
            await db.users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "oauth_providers": providers,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )
            user["oauth_providers"] = providers
        return user

    return await create_user(
        db,
        email,
        name,
        oauth_providers=[{"provider": provider, "provider_id": provider_id}],
    )

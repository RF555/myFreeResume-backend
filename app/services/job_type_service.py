from datetime import datetime, timezone

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.exceptions import NotFoundError


async def create_job_type(db: AsyncDatabase, user_id: str, name: str) -> dict:
    now = datetime.now(timezone.utc)
    doc = {
        "user_id": user_id,
        "name": name,
        "created_at": now,
        "updated_at": now,
    }
    result = await db.job_types.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


async def list_job_types(db: AsyncDatabase, user_id: str) -> list[dict]:
    cursor = db.job_types.find({"user_id": user_id}).sort("created_at", -1)
    return await cursor.to_list()


async def update_job_type(db: AsyncDatabase, user_id: str, job_type_id: str, name: str) -> dict:
    result = await db.job_types.find_one_and_update(
        {"_id": ObjectId(job_type_id), "user_id": user_id},
        {"$set": {"name": name, "updated_at": datetime.now(timezone.utc)}},
        return_document=True,
    )
    if not result:
        raise NotFoundError("Job type not found")
    return result


async def delete_job_type(db: AsyncDatabase, user_id: str, job_type_id: str) -> None:
    result = await db.job_types.delete_one(
        {"_id": ObjectId(job_type_id), "user_id": user_id}
    )
    if result.deleted_count == 0:
        raise NotFoundError("Job type not found")
    await db.entries.delete_many(
        {"user_id": user_id, "job_type_id": job_type_id}
    )

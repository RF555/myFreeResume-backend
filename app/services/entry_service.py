from datetime import datetime, timezone
from copy import deepcopy

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.exceptions import NotFoundError
from app.models.entry import ResumeData, CoverLetterData


async def create_entry(db: AsyncDatabase, user_id: str, job_type_id: str, company_name: str) -> dict:
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    resume_data = deepcopy(user.get("resume_profile", {})) if user else ResumeData().model_dump()
    if not resume_data:
        resume_data = ResumeData().model_dump()

    now = datetime.now(timezone.utc)
    doc = {
        "user_id": user_id,
        "job_type_id": job_type_id,
        "company_name": company_name,
        "resume": resume_data,
        "cover_letter": CoverLetterData().model_dump(),
        "hidden_sections": {},
        "section_order": ["education", "core_competencies", "skill_categories", "skill_highlights", "experience", "languages"],
        "created_at": now,
        "updated_at": now,
    }
    result = await db.entries.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


async def get_entry(db: AsyncDatabase, user_id: str, entry_id: str) -> dict:
    doc = await db.entries.find_one({"_id": ObjectId(entry_id), "user_id": user_id})
    if not doc:
        raise NotFoundError("Entry not found")
    return doc


async def list_entries(db: AsyncDatabase, user_id: str, job_type_id: str) -> list[dict]:
    cursor = db.entries.find(
        {"user_id": user_id, "job_type_id": job_type_id}
    ).sort("created_at", -1)
    return await cursor.to_list()


async def update_entry(db: AsyncDatabase, user_id: str, entry_id: str, updates: dict) -> dict:
    set_fields = {"updated_at": datetime.now(timezone.utc)}
    for key, value in updates.items():
        if value is not None:
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    set_fields[f"{key}.{nested_key}"] = nested_value
            else:
                set_fields[key] = value

    result = await db.entries.find_one_and_update(
        {"_id": ObjectId(entry_id), "user_id": user_id},
        {"$set": set_fields},
        return_document=True,
    )
    if not result:
        raise NotFoundError("Entry not found")
    return result


async def delete_entry(db: AsyncDatabase, user_id: str, entry_id: str) -> None:
    result = await db.entries.delete_one(
        {"_id": ObjectId(entry_id), "user_id": user_id}
    )
    if result.deleted_count == 0:
        raise NotFoundError("Entry not found")


async def refresh_entry_from_profile(db: AsyncDatabase, user_id: str, entry_id: str) -> dict:
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    profile = deepcopy(user.get("resume_profile", {})) if user else {}
    if not profile:
        profile = ResumeData().model_dump()

    result = await db.entries.find_one_and_update(
        {"_id": ObjectId(entry_id), "user_id": user_id},
        {"$set": {"resume": profile, "updated_at": datetime.now(timezone.utc)}},
        return_document=True,
    )
    if not result:
        raise NotFoundError("Entry not found")
    return result


async def clone_entry(db: AsyncDatabase, user_id: str, entry_id: str, target_job_type_id: str, company_name: str) -> dict:
    source = await get_entry(db, user_id, entry_id)
    now = datetime.now(timezone.utc)
    clone_doc = {
        "user_id": user_id,
        "job_type_id": target_job_type_id,
        "company_name": company_name,
        "resume": deepcopy(source["resume"]),
        "cover_letter": deepcopy(source["cover_letter"]),
        "hidden_sections": deepcopy(source.get("hidden_sections", {})),
        "section_order": deepcopy(source.get("section_order", ["skill_highlights", "experience", "education", "languages"])),
        "created_at": now,
        "updated_at": now,
    }
    result = await db.entries.insert_one(clone_doc)
    clone_doc["_id"] = result.inserted_id
    return clone_doc

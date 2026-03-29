from fastapi import APIRouter, Depends, status

from app.database import get_db
from app.dependencies import get_current_user
from app.models.entry import CloneRequest, EntryCreate, EntryResponse, EntryUpdate
from app.services.entry_service import (
    clone_entry,
    create_entry,
    delete_entry,
    get_entry,
    list_entries,
    refresh_entry_from_profile,
    update_entry,
)

router = APIRouter(tags=["entries"])


def _to_response(doc: dict) -> EntryResponse:
    return EntryResponse(
        id=str(doc["_id"]),
        job_type_id=str(doc["job_type_id"]),
        company_name=doc["company_name"],
        resume=doc["resume"],
        cover_letter=doc["cover_letter"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.post(
    "/api/job-types/{job_type_id}/entries",
    response_model=EntryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create(job_type_id: str, data: EntryCreate, user: dict = Depends(get_current_user)):
    db = get_db()
    doc = await create_entry(db, str(user["_id"]), job_type_id, data.company_name)
    return _to_response(doc)


@router.get("/api/job-types/{job_type_id}/entries", response_model=list[EntryResponse])
async def list_all(job_type_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    docs = await list_entries(db, str(user["_id"]), job_type_id)
    return [_to_response(d) for d in docs]


@router.get("/api/entries/{entry_id}", response_model=EntryResponse)
async def get(entry_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    doc = await get_entry(db, str(user["_id"]), entry_id)
    return _to_response(doc)


@router.put("/api/entries/{entry_id}", response_model=EntryResponse)
async def update(entry_id: str, data: EntryUpdate, user: dict = Depends(get_current_user)):
    db = get_db()
    updates = data.model_dump(exclude_unset=True)
    doc = await update_entry(db, str(user["_id"]), entry_id, updates)
    return _to_response(doc)


@router.delete("/api/entries/{entry_id}")
async def delete(entry_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    await delete_entry(db, str(user["_id"]), entry_id)
    return {"message": "Deleted"}


@router.post(
    "/api/entries/{entry_id}/clone",
    response_model=EntryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def clone(entry_id: str, data: CloneRequest, user: dict = Depends(get_current_user)):
    db = get_db()
    doc = await clone_entry(
        db, str(user["_id"]), entry_id, data.job_type_id, data.company_name
    )
    return _to_response(doc)


@router.post("/api/entries/{entry_id}/refresh-from-profile", response_model=EntryResponse)
async def refresh_from_profile(entry_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    doc = await refresh_entry_from_profile(db, str(user["_id"]), entry_id)
    return _to_response(doc)

from fastapi import APIRouter, Depends, status

from app.database import get_db
from app.dependencies import get_current_user
from app.models.job_type import JobTypeCreate, JobTypeResponse, JobTypeUpdate
from app.services.job_type_service import (
    create_job_type,
    delete_job_type,
    list_job_types,
    update_job_type,
)

router = APIRouter(prefix="/api/job-types", tags=["job-types"])


def _to_response(doc: dict) -> JobTypeResponse:
    return JobTypeResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.post("", response_model=JobTypeResponse, status_code=status.HTTP_201_CREATED)
async def create(data: JobTypeCreate, user: dict = Depends(get_current_user)):
    db = get_db()
    doc = await create_job_type(db, str(user["_id"]), data.name)
    return _to_response(doc)


@router.get("", response_model=list[JobTypeResponse])
async def list_all(user: dict = Depends(get_current_user)):
    db = get_db()
    docs = await list_job_types(db, str(user["_id"]))
    return [_to_response(d) for d in docs]


@router.put("/{job_type_id}", response_model=JobTypeResponse)
async def update(job_type_id: str, data: JobTypeUpdate, user: dict = Depends(get_current_user)):
    db = get_db()
    doc = await update_job_type(db, str(user["_id"]), job_type_id, data.name)
    return _to_response(doc)


@router.delete("/{job_type_id}")
async def delete(job_type_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    await delete_job_type(db, str(user["_id"]), job_type_id)
    return {"message": "Deleted"}

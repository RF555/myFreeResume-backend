from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.database import get_db
from app.dependencies import get_current_user
from app.models.entry import CoverLetterData, ResumeData, Contact
from app.services.docx.cover_letter_generator import generate_cover_letter
from app.services.docx.resume_generator import generate_resume
from app.services.entry_service import get_entry

router = APIRouter(prefix="/api/entries", tags=["documents"])

DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@router.get("/{entry_id}/download/resume")
async def download_resume(entry_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    entry = await get_entry(db, str(user["_id"]), entry_id)

    resume_data = ResumeData(**entry["resume"])
    docx_bytes = generate_resume(
        resume_data,
        hidden_sections=entry.get("hidden_sections"),
        section_order=entry.get("section_order"),
    )

    filename = f"{resume_data.name or 'Resume'} - Resume.docx"
    return Response(
        content=docx_bytes,
        media_type=DOCX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{entry_id}/download/cover-letter")
async def download_cover_letter(entry_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    entry = await get_entry(db, str(user["_id"]), entry_id)

    resume_data = ResumeData(**entry["resume"])
    cl_data = CoverLetterData(**entry["cover_letter"])
    contact = resume_data.contact or Contact()

    docx_bytes = generate_cover_letter(
        resume_data.name, resume_data.professional_title, contact, cl_data
    )

    filename = f"{resume_data.name or 'Cover Letter'} - Cover Letter.docx"
    return Response(
        content=docx_bytes,
        media_type=DOCX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

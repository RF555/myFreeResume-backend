import io

from docx import Document
from docx.shared import Pt, Inches

from app.models.entry import CoverLetterData, Contact
from app.services.docx.styles import (
    BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR,
    add_header_band, add_contact_line, set_run_font,
)


def generate_cover_letter(
    name: str,
    professional_title: str,
    contact: Contact,
    data: CoverLetterData,
) -> bytes:
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    add_header_band(doc, name, professional_title)

    contact_dict = contact.model_dump() if contact else {}
    add_contact_line(doc, contact_dict)

    if data.addressee_name or data.addressee_company:
        p = doc.add_paragraph()
        p.space_before = Pt(12)
        to_run = p.add_run("To")
        set_run_font(to_run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR, bold=True)

        if data.addressee_name:
            name_p = doc.add_paragraph()
            run = name_p.add_run(data.addressee_name)
            set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)
            name_p.space_after = Pt(0)

        if data.addressee_company:
            comp_p = doc.add_paragraph()
            run = comp_p.add_run(data.addressee_company)
            set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)
            comp_p.space_after = Pt(6)

    if data.date:
        date_p = doc.add_paragraph()
        date_p.space_before = Pt(12)
        run = date_p.add_run(data.date)
        set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)

    if data.subject:
        subj_p = doc.add_paragraph()
        run = subj_p.add_run(data.subject)
        set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR, bold=True)
        subj_p.space_after = Pt(6)

    for para_text in data.body_paragraphs:
        p = doc.add_paragraph()
        run = p.add_run(para_text)
        set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)
        p.space_after = Pt(6)

    if data.closing:
        closing_p = doc.add_paragraph()
        closing_p.space_before = Pt(12)
        run = closing_p.add_run(data.closing + ",")
        set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)

        sig_p = doc.add_paragraph()
        run = sig_p.add_run(name)
        set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR, bold=True)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

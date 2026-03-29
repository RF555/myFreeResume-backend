import io

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_TAB_ALIGNMENT

from app.models.entry import ResumeData
from app.services.docx.styles import (
    BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR, SMALL_SIZE,
    add_header_band, add_contact_line, add_section_header, set_run_font,
)


def generate_resume(data: ResumeData) -> bytes:
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    add_header_band(doc, data.name, data.professional_title)

    contact_dict = data.contact.model_dump() if data.contact else {}
    add_contact_line(doc, contact_dict)

    if data.summary:
        add_section_header(doc, "Professional Summary")
        p = doc.add_paragraph()
        run = p.add_run(data.summary)
        set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)

    if data.skill_highlights:
        add_section_header(doc, "Skill Highlights")
        for skill in data.skill_highlights:
            p = doc.add_paragraph(style="List Bullet")
            p.clear()
            run = p.add_run(skill)
            set_run_font(run, BODY_FONT, SMALL_SIZE, BODY_TEXT_COLOR)

    if data.experience:
        add_section_header(doc, "Professional Experience")
        for exp in data.experience:
            p = doc.add_paragraph()
            role_run = p.add_run(exp.role)
            set_run_font(role_run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR, bold=True)
            if exp.company:
                sep_run = p.add_run(f"  —  {exp.company}")
                set_run_font(sep_run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)

            if exp.start_date or exp.end_date:
                date_text = f"{exp.start_date} – {exp.end_date}"
                tab_run = p.add_run(f"\t{date_text}")
                set_run_font(tab_run, BODY_FONT, SMALL_SIZE, BODY_TEXT_COLOR)
                tab_stops = p.paragraph_format.tab_stops
                tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT)

            p.space_after = Pt(2)

            for bullet in exp.bullets:
                bp = doc.add_paragraph(style="List Bullet")
                bp.clear()
                run = bp.add_run(bullet)
                set_run_font(run, BODY_FONT, SMALL_SIZE, BODY_TEXT_COLOR)
                bp.space_after = Pt(1)

    if data.education:
        add_section_header(doc, "Education")
        for edu in data.education:
            p = doc.add_paragraph()
            deg_run = p.add_run(edu.degree)
            set_run_font(deg_run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR, bold=True)
            if edu.institution:
                inst_run = p.add_run(f"  —  {edu.institution}")
                set_run_font(inst_run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)

            if edu.start_date or edu.end_date:
                date_text = f"{edu.start_date} – {edu.end_date}"
                tab_run = p.add_run(f"\t{date_text}")
                set_run_font(tab_run, BODY_FONT, SMALL_SIZE, BODY_TEXT_COLOR)
                tab_stops = p.paragraph_format.tab_stops
                tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT)

            p.space_after = Pt(4)

    if data.languages:
        add_section_header(doc, "Languages")
        p = doc.add_paragraph()
        run = p.add_run(", ".join(data.languages))
        set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)

    for cs in data.custom_sections:
        if cs.title:
            add_section_header(doc, cs.title)
            for item in cs.items:
                p = doc.add_paragraph(style="List Bullet")
                p.clear()
                run = p.add_run(item)
                set_run_font(run, BODY_FONT, SMALL_SIZE, BODY_TEXT_COLOR)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

import io

from docx import Document
from docx.shared import Pt

from app.models.entry import ResumeData
from app.services.docx.styles import (
    BODY_FONT, NAVY, BODY_TEXT_COLOR, ROLE_COLOR, PROFILE_COLOR,
    BODY_SIZE,
    setup_page, add_header_band, create_two_column_table,
    add_section_header, add_contact_items, set_run_font,
)

SIDEBAR_SECTIONS = {"contact", "education", "skill_categories", "core_competencies", "skill_highlights"}

DEFAULT_SIDEBAR_ORDER = ["contact", "education", "core_competencies", "skill_categories", "skill_highlights"]
DEFAULT_MAIN_ORDER = ["summary", "experience", "custom_sections"]


def _ordered_sections(section_order: list[str], defaults: list[str], allowed: set[str]) -> list[str]:
    if not section_order:
        return defaults
    ordered = [s for s in section_order if s in allowed]
    for s in defaults:
        if s not in ordered:
            ordered.append(s)
    return ordered


def _add_education(cell, education):
    add_section_header(cell, "Education")
    for edu in education:
        p = cell.add_paragraph()
        if edu.degree:
            deg_run = p.add_run(edu.degree)
            set_run_font(deg_run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR, bold=True)
        rest = ""
        if edu.institution:
            rest += f" | {edu.institution}"
        if edu.end_date:
            rest += f", {edu.end_date}"
        if rest:
            run = p.add_run(rest)
            set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)
        p.space_after = Pt(2)


def _add_skill_categories(cell, skill_categories):
    add_section_header(cell, "Technical Skills")
    for cat in skill_categories:
        p = cell.add_paragraph()
        name_run = p.add_run(cat.name)
        set_run_font(name_run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR, bold=True)
        if cat.skills:
            skills_text = " | " + " | ".join(cat.skills)
            run = p.add_run(skills_text)
            set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)
        p.space_after = Pt(2)


def _add_skill_highlights(cell, skill_highlights, languages):
    add_section_header(cell, "Skill Highlights")
    items = []
    if languages:
        lang_text = "Multilingual — " + ", ".join(languages) if len(languages) > 1 else languages[0]
        items.append(lang_text)
    items.extend(skill_highlights)
    for item in items:
        p = cell.add_paragraph()
        run = p.add_run(item)
        set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)
        p.space_after = Pt(1)


def _add_core_competencies(cell, core_competencies):
    add_section_header(cell, "Core Competencies")
    for item in core_competencies:
        p = cell.add_paragraph()
        run = p.add_run(item)
        set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)
        p.space_after = Pt(1)


def _add_summary(cell, summary):
    add_section_header(cell, "Profile")
    p = cell.add_paragraph()
    run = p.add_run(summary)
    set_run_font(run, BODY_FONT, BODY_SIZE, PROFILE_COLOR)
    p.space_after = Pt(4)


def _add_experience(cell, experience):
    add_section_header(cell, "Relevant Experience")
    for exp in experience:
        p = cell.add_paragraph()
        if exp.role:
            role_run = p.add_run(exp.role)
            set_run_font(role_run, BODY_FONT, Pt(12), ROLE_COLOR, bold=True)
        rest_parts = []
        if exp.company:
            rest_parts.append(exp.company)
        date_str = ""
        if exp.start_date and exp.end_date:
            date_str = f"{exp.start_date} – {exp.end_date}"
        elif exp.start_date:
            date_str = exp.start_date
        elif exp.end_date:
            date_str = exp.end_date
        if date_str:
            rest_parts.append(date_str)
        if rest_parts:
            run = p.add_run(" | " + " | ".join(rest_parts))
            set_run_font(run, BODY_FONT, Pt(12), NAVY)
        p.space_after = Pt(2)

        for bullet in exp.bullets:
            bp = cell.add_paragraph(style="List Bullet")
            bp.clear()
            run = bp.add_run(bullet)
            set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)
            bp.space_after = Pt(1)


def _add_custom_sections(cell, custom_sections):
    for cs in custom_sections:
        if cs.title:
            add_section_header(cell, cs.title)
            for item in cs.items:
                p = cell.add_paragraph(style="List Bullet")
                p.clear()
                run = p.add_run(item)
                set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)
                p.space_after = Pt(1)


def generate_resume(
    data: ResumeData,
    hidden_sections: dict | None = None,
    section_order: list[str] | None = None,
) -> bytes:
    hidden = hidden_sections or {}
    doc = Document()
    setup_page(doc)

    add_header_band(doc, data.name, data.professional_title)

    sidebar, main = create_two_column_table(doc)

    # Clear default empty paragraphs
    for p in sidebar.paragraphs:
        if not p.text:
            p._element.getparent().remove(p._element)
    for p in main.paragraphs:
        if not p.text:
            p._element.getparent().remove(p._element)

    # Sidebar sections
    sidebar_order = _ordered_sections(
        section_order or [], DEFAULT_SIDEBAR_ORDER, SIDEBAR_SECTIONS,
    )
    contact_dict = data.contact.model_dump() if data.contact else {}

    for section_id in sidebar_order:
        if hidden.get(section_id):
            continue
        if section_id == "contact" and any(contact_dict.values()):
            add_section_header(sidebar, "Contact")
            add_contact_items(sidebar, contact_dict)
        elif section_id == "education" and data.education:
            _add_education(sidebar, data.education)
        elif section_id == "skill_categories" and data.skill_categories:
            _add_skill_categories(sidebar, data.skill_categories)
        elif section_id == "core_competencies" and data.core_competencies:
            _add_core_competencies(sidebar, data.core_competencies)
        elif section_id == "skill_highlights" and (data.skill_highlights or data.languages):
            _add_skill_highlights(sidebar, data.skill_highlights, data.languages)

    # Main sections
    main_order = _ordered_sections(
        section_order or [], DEFAULT_MAIN_ORDER, {"summary", "experience", "custom_sections"},
    )

    for section_id in main_order:
        if hidden.get(section_id):
            continue
        if section_id == "summary" and data.summary:
            _add_summary(main, data.summary)
        elif section_id == "experience" and data.experience:
            _add_experience(main, data.experience)
        elif section_id == "custom_sections" and data.custom_sections:
            _add_custom_sections(main, data.custom_sections)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

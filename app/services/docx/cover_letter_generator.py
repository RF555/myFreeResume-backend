import io

from docx import Document
from docx.shared import Pt

from app.models.entry import CoverLetterData, Contact
from app.services.docx.styles import (
    BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR,
    setup_page, add_header_band, create_two_column_table,
    add_section_header, add_contact_items, set_run_font,
)


def generate_cover_letter(
    name: str,
    professional_title: str,
    contact: Contact,
    data: CoverLetterData,
) -> bytes:
    doc = Document()
    setup_page(doc)

    add_header_band(doc, name, professional_title)

    sidebar, main = create_two_column_table(doc)

    # Clear default empty paragraphs
    for p in sidebar.paragraphs:
        if not p.text:
            p._element.getparent().remove(p._element)
    for p in main.paragraphs:
        if not p.text:
            p._element.getparent().remove(p._element)

    # Sidebar: Contact
    contact_dict = contact.model_dump() if contact else {}
    if any(contact_dict.values()):
        add_section_header(sidebar, "Contact")
        add_contact_items(sidebar, contact_dict)

    # Sidebar: To block
    if data.addressee_name or data.addressee_company:
        p = sidebar.add_paragraph()
        p.space_before = Pt(12)
        to_run = p.add_run("To")
        set_run_font(to_run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR, bold=True)

        if data.addressee_name:
            p2 = sidebar.add_paragraph()
            run = p2.add_run(data.addressee_name)
            set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)
            p2.space_after = Pt(0)

        if data.addressee_company:
            p3 = sidebar.add_paragraph()
            run = p3.add_run(data.addressee_company)
            set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)
            p3.space_after = Pt(4)

    # Sidebar: Date block
    if data.date:
        from datetime import datetime as dt
        try:
            date_display = dt.strptime(data.date, "%Y-%m-%d").strftime("%B %d, %Y")
        except ValueError:
            date_display = data.date

        p = sidebar.add_paragraph()
        p.space_before = Pt(8)
        date_label = p.add_run("Date")
        set_run_font(date_label, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR, bold=True)

        p2 = sidebar.add_paragraph()
        run = p2.add_run(date_display)
        set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)

    # Main: Salutation
    if data.salutation:
        add_section_header(main, data.salutation)

    # Main: Body paragraphs
    for para_text in data.body_paragraphs:
        p = main.add_paragraph()
        run = p.add_run(para_text)
        set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)
        p.space_after = Pt(6)

    # Main: Closing + signature
    if data.closing:
        closing_p = main.add_paragraph()
        closing_p.space_before = Pt(12)
        run = closing_p.add_run(data.closing)
        set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR)

        sig_p = main.add_paragraph()
        run = sig_p.add_run(name)
        set_run_font(run, BODY_FONT, BODY_SIZE, BODY_TEXT_COLOR, bold=True)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

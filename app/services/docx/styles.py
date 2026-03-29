from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

NAVY = RGBColor(0x22, 0x4E, 0x76)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BODY_TEXT_COLOR = RGBColor(0x2D, 0x26, 0x2E)

HEADING_FONT = "Century Gothic"
BODY_FONT = "Calibri Light"

NAME_SIZE = Pt(28)
TITLE_SIZE = Pt(14)
SECTION_HEADER_SIZE = Pt(15)
BODY_SIZE = Pt(11)
SMALL_SIZE = Pt(10)


def set_run_font(run, font_name, size, color=BODY_TEXT_COLOR, bold=False):
    run.font.name = font_name
    run.font.size = size
    run.font.color.rgb = color
    run.font.bold = bold


def add_section_header(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text.upper())
    set_run_font(run, HEADING_FONT, SECTION_HEADER_SIZE, NAVY)
    from docx.oxml.ns import qn
    pPr = p._element.get_or_add_pPr()
    pBdr = pPr.makeelement(qn("w:pBdr"), {})
    bottom = pBdr.makeelement(
        qn("w:bottom"),
        {
            qn("w:val"): "single",
            qn("w:sz"): "4",
            qn("w:space"): "1",
            qn("w:color"): "224E76",
        },
    )
    pBdr.append(bottom)
    pPr.append(pBdr)
    p.space_after = Pt(6)
    return p


def add_header_band(doc, name, professional_title):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    cell = table.cell(0, 0)

    from docx.oxml.ns import qn
    shading = cell._element.get_or_add_tcPr().makeelement(
        qn("w:shd"),
        {
            qn("w:val"): "clear",
            qn("w:color"): "auto",
            qn("w:fill"): "224E76",
        },
    )
    cell._element.get_or_add_tcPr().append(shading)

    name_p = cell.paragraphs[0]
    name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name_run = name_p.add_run(name.upper())
    set_run_font(name_run, HEADING_FONT, NAME_SIZE, WHITE)
    name_run.font.small_caps = True
    name_p.space_after = Pt(2)

    title_p = cell.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run(professional_title)
    set_run_font(title_run, HEADING_FONT, TITLE_SIZE, WHITE)
    title_p.space_before = Pt(0)
    title_p.space_after = Pt(8)

    tbl = table._element
    tblPr = tbl.tblPr
    borders = tblPr.makeelement(qn("w:tblBorders"), {})
    for border_name in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        border = borders.makeelement(
            qn(f"w:{border_name}"),
            {qn("w:val"): "none", qn("w:sz"): "0", qn("w:space"): "0", qn("w:color"): "auto"},
        )
        borders.append(border)
    tblPr.append(borders)

    tblW = tblPr.makeelement(qn("w:tblW"), {qn("w:w"): "5000", qn("w:type"): "pct"})
    tblPr.append(tblW)

    return table


def add_contact_line(doc, contact):
    items = []
    if contact.get("email"):
        items.append(contact["email"])
    if contact.get("phone"):
        items.append(contact["phone"])
    if contact.get("linkedin"):
        items.append(contact["linkedin"])
    if contact.get("github"):
        items.append(contact["github"])
    if contact.get("location"):
        items.append(contact["location"])

    if not items:
        return

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    text = "  |  ".join(items)
    run = p.add_run(text)
    set_run_font(run, BODY_FONT, SMALL_SIZE, NAVY)
    p.space_before = Pt(6)
    p.space_after = Pt(6)

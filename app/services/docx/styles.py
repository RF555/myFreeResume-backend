from docx import Document
from docx.shared import Pt, Emu, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

NAVY = RGBColor(0x23, 0x4F, 0x77)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BODY_TEXT_COLOR = RGBColor(0x2D, 0x26, 0x2E)
ROLE_COLOR = RGBColor(0x3B, 0x38, 0x38)
PROFILE_COLOR = RGBColor(0x3B, 0x38, 0x38)
SIDEBAR_BG = "629DD1"

HEADING_FONT = "Century Gothic"
BODY_FONT = "Calibri Light"

NAME_SIZE = Pt(28)
TITLE_SIZE = Pt(14)
SECTION_HEADER_SIZE = Pt(15)
BODY_SIZE = Pt(10)
SMALL_SIZE = Pt(10)
CONTACT_SIZE = Pt(9)

# A4 page in DXA (twentieths of a point)
PAGE_WIDTH = 11906
PAGE_HEIGHT = 16838
MARGIN_TOP = 630
MARGIN_RIGHT = 282
MARGIN_BOTTOM = 1440
MARGIN_LEFT = 1440

CONTENT_WIDTH = PAGE_WIDTH  # Table spans full page width (edge to edge)
SIDEBAR_WIDTH = CONTENT_WIDTH * 2 // 5  # 40%
MAIN_WIDTH = CONTENT_WIDTH - SIDEBAR_WIDTH


def _dxa_to_emu(dxa: int) -> int:
    return dxa * 914400 // 1440


def set_run_font(run, font_name, size, color=BODY_TEXT_COLOR, bold=False):
    run.font.name = font_name
    run.font.size = size
    run.font.color.rgb = color
    run.font.bold = bold


def setup_page(doc: Document):
    for section in doc.sections:
        section.page_width = Emu(_dxa_to_emu(PAGE_WIDTH))
        section.page_height = Emu(_dxa_to_emu(PAGE_HEIGHT))
        section.top_margin = Emu(0)
        section.bottom_margin = Emu(_dxa_to_emu(MARGIN_BOTTOM))
        section.left_margin = Emu(_dxa_to_emu(MARGIN_LEFT))
        section.right_margin = Emu(0)


def _set_cell_shading(cell, color_hex: str):
    tcPr = cell._element.get_or_add_tcPr()
    shading = tcPr.makeelement(
        qn("w:shd"),
        {qn("w:val"): "clear", qn("w:color"): "auto", qn("w:fill"): color_hex},
    )
    tcPr.append(shading)


def _remove_table_borders(table):
    tbl = table._element
    tblPr = tbl.tblPr
    borders = tblPr.makeelement(qn("w:tblBorders"), {})
    for name in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        border = borders.makeelement(
            qn(f"w:{name}"),
            {qn("w:val"): "none", qn("w:sz"): "0", qn("w:space"): "0", qn("w:color"): "auto"},
        )
        borders.append(border)
    tblPr.append(borders)


def _set_table_full_width(table):
    tbl = table._element
    tblPr = tbl.tblPr
    # Table width = full page width (edge to edge)
    existing = tblPr.find(qn("w:tblW"))
    if existing is not None:
        tblPr.remove(existing)
    tblW = tblPr.makeelement(qn("w:tblW"), {qn("w:w"): str(CONTENT_WIDTH), qn("w:type"): "dxa"})
    tblPr.append(tblW)
    # Negative indent to pull table into the left margin
    existing_ind = tblPr.find(qn("w:tblInd"))
    if existing_ind is not None:
        tblPr.remove(existing_ind)
    tblInd = tblPr.makeelement(qn("w:tblInd"), {qn("w:w"): str(-MARGIN_LEFT), qn("w:type"): "dxa"})
    tblPr.append(tblInd)
    # Zero default cell margins at table level (override TableNormal's 108 DXA)
    existing_cm = tblPr.find(qn("w:tblCellMar"))
    if existing_cm is not None:
        tblPr.remove(existing_cm)
    cellMar = tblPr.makeelement(qn("w:tblCellMar"), {})
    for side in ["top", "left", "bottom", "right"]:
        m = cellMar.makeelement(qn(f"w:{side}"), {qn("w:w"): "0", qn("w:type"): "dxa"})
        cellMar.append(m)
    tblPr.append(cellMar)
    # Fixed layout for precise column widths
    existing_layout = tblPr.find(qn("w:tblLayout"))
    if existing_layout is not None:
        tblPr.remove(existing_layout)
    layout = tblPr.makeelement(qn("w:tblLayout"), {qn("w:type"): "fixed"})
    tblPr.append(layout)


def _set_cell_width(cell, width_dxa: int):
    tcPr = cell._element.get_or_add_tcPr()
    existing = tcPr.find(qn("w:tcW"))
    if existing is not None:
        tcPr.remove(existing)
    tcW = tcPr.makeelement(qn("w:tcW"), {qn("w:w"): str(width_dxa), qn("w:type"): "dxa"})
    tcPr.append(tcW)


def _set_cell_margins(cell, top=0, bottom=0, left=0, right=0):
    tcPr = cell._element.get_or_add_tcPr()
    margins = tcPr.makeelement(qn("w:tcMar"), {})
    for side, val in [("top", top), ("bottom", bottom), ("start", left), ("end", right)]:
        m = margins.makeelement(qn(f"w:{side}"), {qn("w:w"): str(val), qn("w:type"): "dxa"})
        margins.append(m)
    tcPr.append(margins)


def _set_grid_columns(table, widths: list[int]):
    tblGrid = table._element.find(qn("w:tblGrid"))
    if tblGrid is not None:
        table._element.remove(tblGrid)
    tblGrid = table._element.makeelement(qn("w:tblGrid"), {})
    for w in widths:
        col = tblGrid.makeelement(qn("w:gridCol"), {qn("w:w"): str(w)})
        tblGrid.append(col)
    table._element.insert(1, tblGrid)


def add_no_border_table(doc, rows, cols):
    table = doc.add_table(rows=rows, cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    _remove_table_borders(table)
    _set_table_full_width(table)
    return table


def add_header_band(doc, name: str, professional_title: str):
    table = add_no_border_table(doc, 1, 1)
    _set_grid_columns(table, [CONTENT_WIDTH])
    cell = table.cell(0, 0)
    _set_cell_width(cell, CONTENT_WIDTH)
    _set_cell_shading(cell, SIDEBAR_BG)
    _set_cell_margins(cell, top=80, bottom=80, left=120, right=120)

    name_p = cell.paragraphs[0]
    name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name_run = name_p.add_run(name.upper())
    set_run_font(name_run, HEADING_FONT, NAME_SIZE, WHITE)
    name_p.space_after = Pt(2)

    title_p = cell.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run(professional_title)
    set_run_font(title_run, HEADING_FONT, TITLE_SIZE, WHITE)
    title_p.space_before = Pt(0)
    title_p.space_after = Pt(4)

    return table


def create_two_column_table(doc):
    table = add_no_border_table(doc, 1, 2)
    _set_grid_columns(table, [SIDEBAR_WIDTH, MAIN_WIDTH])

    sidebar = table.cell(0, 0)
    main = table.cell(0, 1)

    _set_cell_width(sidebar, SIDEBAR_WIDTH)
    _set_cell_width(main, MAIN_WIDTH)
    _set_cell_shading(sidebar, SIDEBAR_BG)
    _set_cell_margins(sidebar, top=80, bottom=80, left=360, right=120)
    _set_cell_margins(main, top=80, bottom=80, left=200, right=0)

    return sidebar, main


def add_section_header(cell, text: str):
    p = cell.add_paragraph()
    run = p.add_run(text.upper())
    set_run_font(run, HEADING_FONT, SECTION_HEADER_SIZE, NAVY)
    p.space_before = Pt(8)
    p.space_after = Pt(4)
    return p


def add_contact_items(cell, contact: dict):
    order = ["location", "phone", "email", "linkedin", "github"]
    for key in order:
        val = contact.get(key, "")
        if val:
            p = cell.add_paragraph()
            run = p.add_run(val)
            set_run_font(run, BODY_FONT, CONTACT_SIZE, BODY_TEXT_COLOR)
            p.space_after = Pt(1)
            p.space_before = Pt(0)

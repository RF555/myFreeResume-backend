import io
from docx import Document

from app.services.docx.cover_letter_generator import generate_cover_letter
from app.models.entry import CoverLetterData, Contact


def test_generate_cover_letter_returns_bytes():
    data = CoverLetterData(
        addressee_name="Jane Smith",
        addressee_company="Google",
        date="March 25, 2026",
        subject="Re: Software Engineer Position",
        body_paragraphs=[
            "I am writing to express my interest in the Software Engineer position.",
            "With 5 years of experience in building scalable applications...",
            "I look forward to discussing how I can contribute to your team.",
        ],
        closing="Best regards",
    )
    contact = Contact(email="john@example.com", phone="+1234567890", location="New York, NY")
    result = generate_cover_letter("John Doe", "Software Engineer", contact, data)
    assert isinstance(result, bytes)
    doc = Document(io.BytesIO(result))
    assert len(doc.paragraphs) > 0


def test_generate_cover_letter_contains_addressee():
    data = CoverLetterData(
        addressee_name="Bob Jones",
        addressee_company="Acme Corp",
        body_paragraphs=["Hello"],
        closing="Sincerely",
    )
    contact = Contact()
    result = generate_cover_letter("Alice", "Dev", contact, data)
    doc = Document(io.BytesIO(result))
    full_text = "\n".join([p.text for p in doc.paragraphs])
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                full_text += "\n" + cell.text
    assert "Bob Jones" in full_text
    assert "Acme Corp" in full_text

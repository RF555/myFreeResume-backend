import io
from docx import Document

from app.services.docx.resume_generator import generate_resume
from app.models.entry import ResumeData, Contact, ExperienceItem, EducationItem


def test_generate_resume_returns_bytes():
    data = ResumeData(
        name="John Doe",
        professional_title="Software Engineer",
        summary="Experienced developer with 5 years of experience.",
        contact=Contact(email="john@example.com", phone="+1234567890", location="New York, NY"),
        skill_highlights=["Python", "React", "FastAPI"],
        experience=[
            ExperienceItem(
                company="Google", role="Senior Engineer",
                start_date="2020", end_date="Present",
                bullets=["Led team of 5", "Built microservices"],
            )
        ],
        education=[
            EducationItem(institution="MIT", degree="B.S. Computer Science", start_date="2014", end_date="2018")
        ],
        languages=["English", "Spanish"],
    )
    result = generate_resume(data)
    assert isinstance(result, bytes)
    doc = Document(io.BytesIO(result))
    assert len(doc.paragraphs) > 0


def test_generate_resume_contains_name():
    data = ResumeData(name="Jane Smith", professional_title="Designer")
    result = generate_resume(data)
    doc = Document(io.BytesIO(result))
    all_text = "\n".join([p.text for p in doc.paragraphs])
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                all_text += "\n" + cell.text
    assert "JANE SMITH" in all_text


def test_generate_resume_empty_data():
    data = ResumeData()
    result = generate_resume(data)
    assert isinstance(result, bytes)

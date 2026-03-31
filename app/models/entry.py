from datetime import datetime

from pydantic import BaseModel, Field


class Contact(BaseModel):
    phone: str = Field(default="", max_length=50)
    email: str = Field(default="", max_length=200)
    linkedin: str = Field(default="", max_length=500)
    github: str = Field(default="", max_length=500)
    location: str = Field(default="", max_length=200)


class ExperienceItem(BaseModel):
    company: str = Field(default="", max_length=200)
    role: str = Field(default="", max_length=200)
    start_date: str = Field(default="", max_length=50)
    end_date: str = Field(default="", max_length=50)
    bullets: list[str] = []


class EducationItem(BaseModel):
    institution: str = Field(default="", max_length=200)
    degree: str = Field(default="", max_length=200)
    start_date: str = Field(default="", max_length=50)
    end_date: str = Field(default="", max_length=50)


class CustomSection(BaseModel):
    title: str = Field(default="", max_length=200)
    items: list[str] = []


class SkillCategory(BaseModel):
    name: str = Field(default="", max_length=200)
    skills: list[str] = []


class ResumeData(BaseModel):
    name: str = Field(default="", max_length=200)
    professional_title: str = Field(default="", max_length=200)
    summary: str = Field(default="", max_length=5000)
    contact: Contact = Contact()
    skill_highlights: list[str] = []
    skill_categories: list[SkillCategory] = []
    core_competencies: list[str] = []
    experience: list[ExperienceItem] = []
    education: list[EducationItem] = []
    languages: list[str] = []
    custom_sections: list[CustomSection] = []


class CoverLetterData(BaseModel):
    addressee_name: str = Field(default="", max_length=200)
    addressee_company: str = Field(default="", max_length=200)
    date: str = Field(default="", max_length=50)
    salutation: str = Field(default="", max_length=500)
    body_paragraphs: list[str] = []
    closing: str = Field(default="", max_length=200)


class EntryCreate(BaseModel):
    company_name: str = Field(min_length=1, max_length=200)


class EntryUpdate(BaseModel):
    company_name: str | None = None
    resume: ResumeData | None = None
    cover_letter: CoverLetterData | None = None
    hidden_sections: dict | None = None
    section_order: list[str] | None = None


class EntryResponse(BaseModel):
    id: str
    job_type_id: str
    company_name: str
    resume: ResumeData
    cover_letter: CoverLetterData
    hidden_sections: dict = {}
    section_order: list[str] = []
    created_at: datetime
    updated_at: datetime


class CloneRequest(BaseModel):
    job_type_id: str
    company_name: str = Field(min_length=1, max_length=200)

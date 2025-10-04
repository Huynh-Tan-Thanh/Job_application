from __future__ import annotations

import io
import re
from typing import List, Optional, Tuple

import pdfplumber
from docx import Document
from fastapi import UploadFile

SKILL_KEYWORDS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "node",
    "sql",
    "postgresql",
    "mysql",
    "fastapi",
    "django",
    "flask",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "terraform",
    "kafka",
    "spark",
    "pandas",
    "numpy",
}


def _extract_pdf_text(content: bytes) -> str:
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def _extract_docx_text(content: bytes) -> str:
    document = Document(io.BytesIO(content))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def extract_skills(raw_text: str) -> List[str]:
    tokens = set(re.findall(r"[a-zA-Z\+\#\.]{2,}", raw_text.lower()))
    return sorted(skill for skill in SKILL_KEYWORDS if skill in tokens)


def _guess_name(text: str) -> Optional[str]:
    for line in text.splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        words = candidate.split()
        if 2 <= len(words) <= 6 and all(part[0].isalpha() for part in words if part):
            return candidate
    return None


async def parse_cv(file: UploadFile) -> Tuple[Optional[str], str, List[str]]:
    content = await file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".pdf"):
        text = _extract_pdf_text(content)
    elif filename.endswith(".docx") or filename.endswith(".doc"):
        text = _extract_docx_text(content)
    else:
        raise ValueError("Unsupported file type. Please upload PDF or DOCX files.")

    text = text or ""
    skills = extract_skills(text)
    name_guess = _guess_name(text)
    return name_guess, text, skills

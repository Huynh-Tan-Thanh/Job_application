import io, re
from fastapi import UploadFile
from typing import Tuple, List, Optional
from pdfminer.high_level import extract_text as pdf_text

SKILL_DICT = {"python","java","javascript","react","node","sql","postgresql","fastapi","docker","aws","gcp","kubernetes"}

async def parse_cv(file: UploadFile) -> Tuple[Optional[str], str, List[str]]:
    content = await file.read()
    text = ""
    if file.filename.lower().endswith(".pdf"):
        text = pdf_text(io.BytesIO(content))
    else:
        try:
            import docx2txt
            text = docx2txt.process(io.BytesIO(content))
        except Exception:
            text = content.decode("utf-8", errors="ignore")

    # Heuristic name (dòng đầu không quá dài)
    first_line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    name_guess = first_line if 2 <= len(first_line.split()) <= 6 else None

    # Extract skills (thường hóa)
    tokens = set(re.findall(r"[a-zA-Z\+\#\.]{2,}", text.lower()))
    skills = sorted(list(tokens & SKILL_DICT))
    return name_guess, text, skills

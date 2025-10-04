from __future__ import annotations

from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base
from .types import SkillList


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    cv_text: Mapped[str | None] = mapped_column(Text)
    skills: Mapped[list[str]] = mapped_column(SkillList(), default=list)

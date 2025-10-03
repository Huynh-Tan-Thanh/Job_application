from sqlalchemy import Column, Integer, String, Text
from .database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY

class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    cv_text: Mapped[str | None] = mapped_column(Text)
    # ARRAY(Text) cần PostgreSQL; nếu dùng SQLite dev, đổi sang JSON
    skills: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[])
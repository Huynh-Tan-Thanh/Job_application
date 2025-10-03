from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Text
from sqlalchemy.dialects.postgresql import ARRAY
from .database import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    company: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(Text, nullable=False)
    skills: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[])

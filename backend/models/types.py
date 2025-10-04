from __future__ import annotations

import json
from typing import Any

from sqlalchemy import JSON, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import TypeDecorator


class SkillList(TypeDecorator):
    """Map Python list[str] to ARRAY on Postgres and JSON elsewhere."""

    impl = ARRAY(Text)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(Text))
        return dialect.type_descriptor(JSON)

    def process_bind_param(self, value: Any, dialect):
        return self._ensure_list(value)

    def process_result_value(self, value: Any, dialect):
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value if item is not None]
        if isinstance(value, str):
            try:
                decoded = json.loads(value)
            except json.JSONDecodeError:
                decoded = [part.strip() for part in value.split(",") if part.strip()]
            return [str(item) for item in decoded if item is not None]
        return []

    @staticmethod
    def _ensure_list(value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value if item is not None]
        if isinstance(value, str):
            try:
                decoded = json.loads(value)
            except json.JSONDecodeError:
                decoded = [part.strip() for part in value.split(",") if part.strip()]
            return [str(item) for item in decoded if item is not None]
        return [str(value)]

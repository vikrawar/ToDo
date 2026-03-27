"""
Pydantic models describing the shape of JSON bodies we accept and responses we
return. FastAPI uses them for validation.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TodoCreate(BaseModel):
    """Body for POST /api/todos — only the title comes from the client."""

    title: str = Field(description="Trimmed on the server; whitespace-only is rejected.")

    @field_validator("title")
    @classmethod
    def strip_and_non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Title cannot be empty")
        return cleaned


class TodoUpdate(BaseModel):
    """Body for PATCH /api/todos/{id} — toggle completion."""

    completed: bool


class TodoRead(BaseModel):
    """One todo as returned by the API (GET list and after mutations)."""

    id: int
    title: str
    completed: bool
    created_at: str
    completed_at: Optional[str]

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Component(BaseModel):
    type: str
    name: Optional[str] = None
    label: Optional[str] = None
    required: Optional[bool] = None
    children: Optional[List["Component"]] = None  # Form wraps input components
    model_config = {"extra": "allow"}


class Layout(BaseModel):
    type: str = "SingleColumnLayout"
    children: List[Component]


class Screen(BaseModel):
    id: str
    title: str
    data: Dict[str, Any] = {}
    layout: Layout
    terminal: bool = False


class Flow(BaseModel):
    version: str = "7.2"
    screens: List[Screen]

    def screen_ids(self) -> List[str]:
        return [s.id for s in self.screens]


# ── API ───────────────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=2000)
    max_retries: int = Field(default=3, ge=1, le=5)
    current_flow: Optional[Dict[str, Any]] = None  # if set, modify instead of create


class GenerateResponse(BaseModel):
    flow: Dict[str, Any]
    retries_used: int
    valid: bool
    message: str = ""


class ValidateRequest(BaseModel):
    flow: Dict[str, Any]


class ValidateResponse(BaseModel):
    valid: bool
    errors: List[str] = []

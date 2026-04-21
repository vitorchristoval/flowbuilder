"""Self-healing correction chain."""
from __future__ import annotations
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.prompts.templates import CORRECTION_TEMPLATE


def _extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        inner = lines[1:] if lines[0].startswith("```") else lines
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        text = "\n".join(inner).strip()
    return text


def correct_flow(broken_json: str, errors: str, llm: ChatOpenAI) -> str:
    prompt_text = (
        CORRECTION_TEMPLATE
        .replace("{errors}", errors)
        .replace("{json}", broken_json)
    )
    response = llm.invoke([HumanMessage(content=prompt_text)])
    return _extract_json(response.content)

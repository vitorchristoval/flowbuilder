"""RAG-based flow generation and editing chain."""
from __future__ import annotations
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document

from app.prompts.templates import SYSTEM_PROMPT, GENERATION_TEMPLATE, EDIT_TEMPLATE
from app.rag import get_retriever


def _format_context(docs: list[Document]) -> str:
    return "\n\n---\n\n".join(d.page_content for d in docs)


def _extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        inner = lines[1:] if lines[0].startswith("```") else lines
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        text = "\n".join(inner).strip()
    return text


def generate_flow(user_input: str, llm: ChatOpenAI, current_flow: dict | None = None) -> str:
    retriever = get_retriever(k=5)
    context_docs = retriever.invoke(user_input)
    context = _format_context(context_docs)

    if current_flow:
        prompt_text = (
            EDIT_TEMPLATE
            .replace("{system}", SYSTEM_PROMPT)
            .replace("{context}", context)
            .replace("{current_flow}", json.dumps(current_flow, indent=2))
            .replace("{user_input}", user_input)
        )
    else:
        prompt_text = (
            GENERATION_TEMPLATE
            .replace("{system}", SYSTEM_PROMPT)
            .replace("{context}", context)
            .replace("{user_input}", user_input)
        )

    response = llm.invoke([HumanMessage(content=prompt_text)])
    return _extract_json(response.content)

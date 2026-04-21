"""Loads knowledge base docs and examples into LangChain Documents."""
import json
from pathlib import Path
from langchain_core.documents import Document

KNOWLEDGE_ROOT = Path(__file__).parents[2] / "knowledge"


def _load_json_file(path: Path) -> str:
    return json.dumps(json.loads(path.read_text(encoding="utf-8")), indent=2)


def load_documents() -> list[Document]:
    docs: list[Document] = []

    for json_file in (KNOWLEDGE_ROOT / "docs").glob("*.json"):
        items = json.loads(json_file.read_text(encoding="utf-8"))
        if not isinstance(items, list):
            items = [items]
        for item in items:
            docs.append(
                Document(
                    page_content=json.dumps(item, indent=2),
                    metadata={"source": json_file.name, "type": "component_doc"},
                )
            )

    for json_file in (KNOWLEDGE_ROOT / "examples").glob("*.json"):
        docs.append(
            Document(
                page_content=_load_json_file(json_file),
                metadata={"source": json_file.name, "type": "example"},
            )
        )

    return docs

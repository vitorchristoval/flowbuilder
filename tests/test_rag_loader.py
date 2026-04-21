"""Tests for the RAG document loader (no OpenAI calls)."""
from app.rag.loader import load_documents


def test_loader_returns_documents():
    docs = load_documents()
    assert len(docs) > 0


def test_loader_has_component_docs():
    docs = load_documents()
    component_docs = [d for d in docs if d.metadata.get("type") == "component_doc"]
    assert len(component_docs) >= 5


def test_loader_has_examples():
    docs = load_documents()
    examples = [d for d in docs if d.metadata.get("type") == "example"]
    assert len(examples) >= 3

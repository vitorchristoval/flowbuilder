"""Build and cache a FAISS vector store from the knowledge base."""
from __future__ import annotations
from functools import lru_cache
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .loader import load_documents


@lru_cache(maxsize=1)
def get_vectorstore() -> FAISS:
    docs = load_documents()

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return FAISS.from_documents(chunks, embeddings)


def get_retriever(k: int = 5):
    return get_vectorstore().as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )

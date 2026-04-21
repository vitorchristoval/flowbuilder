"""FastAPI application."""
from __future__ import annotations
import json
import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from app.models import (
    Flow,
    GenerateRequest,
    GenerateResponse,
    ValidateRequest,
    ValidateResponse,
)
from app.pipeline import run_pipeline
from app.rag import get_vectorstore  # warm-up on startup

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Building RAG vector store…")
    get_vectorstore()
    logger.info("Vector store ready.")
    yield


app = FastAPI(
    title="FlowBuilder AI",
    description="Converts natural language to valid WhatsApp Flow JSON using RAG + LangChain",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_llm() -> ChatOpenAI:
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    return ChatOpenAI(model=model, temperature=0.2)


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    """Generate a WhatsApp Flow from a natural language description."""
    llm = _get_llm()
    try:
        flow_dict, retries = run_pipeline(
            user_input=request.prompt,
            llm=llm,
            max_retries=request.max_retries,
            current_flow=request.current_flow,
        )
        return GenerateResponse(
            flow=flow_dict,
            retries_used=retries,
            valid=True,
            message="Flow generated successfully.",
        )
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during generation")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate", response_model=ValidateResponse)
async def validate(request: ValidateRequest) -> ValidateResponse:
    """Validate a WhatsApp Flow JSON against the schema."""
    try:
        Flow.model_validate(request.flow)
        return ValidateResponse(valid=True)
    except ValidationError as e:
        errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        return ValidateResponse(valid=False, errors=errors)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

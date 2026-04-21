"""
Quick smoke test — requires OPENAI_API_KEY in environment.

Usage:
    python scripts/smoke_test.py
"""
import json
import os
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parents[1]))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.pipeline import run_pipeline
from app.models import Flow

load_dotenv()

TEST_PROMPTS = [
    "Simple appointment booking",
    "Multi-step lead capture with interests",
    "Customer support ticket with issue type and description",
    "Incomplete flow — just collect email",  # test inference
]

if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not set")
    sys.exit(1)

llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o"), temperature=0.2)

results = []
for prompt in TEST_PROMPTS:
    print(f"\n{'='*60}")
    print(f"Prompt: {prompt}")
    try:
        flow_dict, retries = run_pipeline(prompt, llm, max_retries=3)
        flow = Flow.model_validate(flow_dict)
        print(f"  ✅  Valid — {len(flow.screens)} screens, {retries} retries")
        results.append({"prompt": prompt, "valid": True, "retries": retries, "screens": len(flow.screens)})
    except Exception as e:
        print(f"  ❌  Failed: {e}")
        results.append({"prompt": prompt, "valid": False, "error": str(e)})

print(f"\n{'='*60}")
total = len(results)
passed = sum(1 for r in results if r["valid"])
print(f"Results: {passed}/{total} valid on first/corrected pass")
avg_retries = sum(r.get("retries", 0) for r in results if r["valid"]) / max(passed, 1)
print(f"Avg retries (valid only): {avg_retries:.2f}")

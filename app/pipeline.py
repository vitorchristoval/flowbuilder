"""Orchestration: generate → validate → auto-correct loop."""
from __future__ import annotations
import json
import logging
from pydantic import ValidationError

from app.models import Flow
from app.chains import generate_flow, correct_flow

logger = logging.getLogger(__name__)


def _validate(json_str: str) -> tuple[bool, str]:
    try:
        Flow.model_validate_json(json_str)
        return True, ""
    except ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, f"JSON parse error: {e}"


def run_pipeline(
    user_input: str,
    llm,
    max_retries: int = 3,
    current_flow: dict | None = None,
) -> tuple[dict, int]:
    last_json = ""
    last_error = ""

    for attempt in range(max_retries):
        if attempt == 0:
            raw = generate_flow(user_input, llm, current_flow=current_flow)
        else:
            logger.warning("Correction attempt %d. Error: %s", attempt, last_error)
            raw = correct_flow(last_json, last_error, llm)

        last_json = raw
        valid, error = _validate(raw)

        if valid:
            return json.loads(raw), attempt

        last_error = error

    raise RuntimeError(
        f"Flow generation failed after {max_retries} attempts. "
        f"Last error: {last_error}"
    )

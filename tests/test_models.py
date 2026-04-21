"""Unit tests for Pydantic schema validation."""
import pathlib
import pytest
from pydantic import ValidationError
from app.models import Flow


VALID_FLOW = {
    "version": "5.1",
    "screens": [
        {
            "id": "FORM",
            "title": "Contact Form",
            "terminal": False,
            "layout": {
                "type": "SingleColumnLayout",
                "children": [
                    {"type": "TextInput", "id": "name", "label": "Name", "required": True},
                    {
                        "type": "Footer",
                        "label": "Submit",
                        "on-click-action": {
                            "name": "navigate",
                            "next": {"type": "screen", "name": "DONE"},
                            "payload": {},
                        },
                    },
                ],
            },
        },
        {
            "id": "DONE",
            "title": "Done",
            "terminal": True,
            "layout": {
                "type": "SingleColumnLayout",
                "children": [
                    {"type": "TextHeading", "text": "Thank you!"},
                    {
                        "type": "Footer",
                        "label": "Close",
                        "on-click-action": {"name": "complete", "payload": {}},
                    },
                ],
            },
        },
    ],
}


def test_valid_flow():
    flow = Flow.model_validate(VALID_FLOW)
    assert len(flow.screens) == 2
    assert flow.screen_ids() == ["FORM", "DONE"]


def test_version():
    flow = Flow.model_validate(VALID_FLOW)
    assert flow.version == "5.1"


def test_missing_screens():
    with pytest.raises(ValidationError):
        Flow.model_validate({"version": "5.1"})


def test_missing_layout():
    bad = {
        "version": "5.1",
        "screens": [{"id": "S1", "title": "T", "terminal": True, "components": []}],
    }
    with pytest.raises(ValidationError):
        Flow.model_validate(bad)


def test_example_appointment():
    flow = Flow.model_validate_json(
        pathlib.Path("knowledge/examples/appointment.json").read_text()
    )
    assert len(flow.screens) >= 2
    assert flow.screens[-1].terminal is True


def test_example_lead_capture():
    flow = Flow.model_validate_json(
        pathlib.Path("knowledge/examples/lead_capture.json").read_text()
    )
    assert flow.screens[-1].terminal is True


def test_example_support():
    flow = Flow.model_validate_json(
        pathlib.Path("knowledge/examples/support.json").read_text()
    )
    assert flow.screens[-1].terminal is True

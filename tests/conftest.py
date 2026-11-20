"""Shared test helpers.

FAKE CLAUDE: tests never call the real Claude API (that costs money and needs a
key). Instead they swap in a pretend Claude whose answers we script by hand.
"""

import pytest

from agent.config import PROJECT_DIR

SAMPLE_TEXT = (PROJECT_DIR / "samples" / "sample_release_FICTIONAL.txt").read_text(encoding="utf-8")


def good_extraction() -> dict:
    def fig(metric, value, quote, scale="thousands"):
        return {"metric": metric, "found": True, "printed_value": value, "scale": scale,
                "basis": "gaap", "source_quote": quote}
    return {
        "company_name": "Example Devices Corp.", "fiscal_year": 2026, "fiscal_quarter": 3,
        "figures": [
            fig("revenue", "165,512", "Total net sales | 165,512 | 146,365"),
            fig("operating_income", "18,922", "Operating income | 18,922 | 11,745"),
            fig("net_income", "14,196", "Net income | $ | 14,196 | $ | 7,133"),
            fig("diluted_eps", "1.42", "Diluted | $ | 1.42 | $ | 0.71", "ones"),
        ],
    }


def good_classification() -> dict:
    growth = "Sales growth was driven by record demand for our new devices and a 14.6% increase in services revenue"
    return {
        "drivers": [
            {"metric": "revenue", "explanation": "Device demand and services growth.", "kind": "recurring", "source_quote": growth},
            {"metric": "net_income", "explanation": "Sales growth and cost control.", "kind": "recurring", "source_quote": growth},
            {"metric": "diluted_eps", "explanation": "Sales growth and cost control.", "kind": "recurring", "source_quote": growth},
        ],
        "guidance": {"status": "raised", "summary": "Q4 net sales outlook raised to about $170 million.",
                     "source_quote": "The company is raising its outlook."},
    }


@pytest.fixture
def fake_claude(monkeypatch):
    """Use as:  fake_claude(extraction_dict, classification_dict)"""
    def install(extraction, classification):
        def pretend(system_prompt, user_message, form_name, form_schema):
            return extraction if form_name == "record_figures" else classification
        monkeypatch.setattr("agent.extract.ask_claude", pretend)
        monkeypatch.setattr("agent.classify.ask_claude", pretend)
    return install

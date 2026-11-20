"""The shapes of the data that move through the agent.

Two jobs:
  1. METRICS lists the numbers the agent looks for. Change this list to change
     what the agent covers.
  2. The classes below describe exactly what Claude must send back. If Claude's
     answer doesn't fit the shape, the program stops instead of guessing.
"""

from typing import Literal

from pydantic import BaseModel

# metric key -> how it is described to Claude and what unit we store it in.
# "USD millions" metrics are converted by code from whatever scale the release prints.
METRICS = {
    "revenue": {
        "label": "Total revenue",
        "unit": "USD millions",
        "definition": "Total revenue for the quarter. Some companies call it total net sales or net revenues.",
    },
    "operating_income": {
        "label": "Operating income",
        "unit": "USD millions",
        "definition": "GAAP operating income (income from operations) for the quarter.",
    },
    "net_income": {
        "label": "Net income",
        "unit": "USD millions",
        "definition": "GAAP net income for the quarter (attributable to the company, if both are shown).",
    },
    "diluted_eps": {
        "label": "Diluted EPS",
        "unit": "USD per share",
        "definition": "GAAP diluted earnings per share for the quarter.",
    },
}

# The two metrics that drive the overall call.
KEY_METRICS = ["diluted_eps", "revenue"]

Scale = Literal["ones", "thousands", "millions", "billions"]


class ExtractedFigure(BaseModel):
    metric: str
    found: bool
    printed_value: str = ""   # the number exactly as printed, e.g. "165,512" or "(3.2)"
    scale: Scale = "ones"     # what the release says the number is "in"
    basis: Literal["gaap", "adjusted", "unknown"] = "unknown"
    source_quote: str = ""    # the line copied word for word from the release


class Extraction(BaseModel):
    company_name: str
    fiscal_year: int
    fiscal_quarter: int
    figures: list[ExtractedFigure]


class Driver(BaseModel):
    metric: str
    explanation: str
    kind: Literal["recurring", "one_time", "unclear"]
    source_quote: str = ""


class Guidance(BaseModel):
    status: Literal["raised", "lowered", "maintained", "introduced", "withdrawn", "not_given"]
    summary: str = ""
    source_quote: str = ""


class Classification(BaseModel):
    drivers: list[Driver]
    guidance: Guidance


# ---- The same shapes, written in the format the Claude API expects -----------
_QUOTE = {"type": "string", "description": "Copied word for word from the document. Empty if none."}

EXTRACTION_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "company_name": {"type": "string"},
        "fiscal_year": {"type": "integer"},
        "fiscal_quarter": {"type": "integer", "description": "1, 2, 3 or 4"},
        "figures": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "metric": {"type": "string", "enum": list(METRICS)},
                    "found": {"type": "boolean"},
                    "printed_value": {"type": "string", "description": "The number exactly as printed."},
                    "scale": {"type": "string", "enum": ["ones", "thousands", "millions", "billions"]},
                    "basis": {"type": "string", "enum": ["gaap", "adjusted", "unknown"]},
                    "source_quote": _QUOTE,
                },
                "required": ["metric", "found", "printed_value", "scale", "basis", "source_quote"],
            },
        },
    },
    "required": ["company_name", "fiscal_year", "fiscal_quarter", "figures"],
}

CLASSIFICATION_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "drivers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "metric": {"type": "string", "enum": list(METRICS)},
                    "explanation": {"type": "string"},
                    "kind": {"type": "string", "enum": ["recurring", "one_time", "unclear"]},
                    "source_quote": _QUOTE,
                },
                "required": ["metric", "explanation", "kind", "source_quote"],
            },
        },
        "guidance": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["raised", "lowered", "maintained", "introduced", "withdrawn", "not_given"],
                },
                "summary": {"type": "string"},
                "source_quote": _QUOTE,
            },
            "required": ["status", "summary", "source_quote"],
        },
    },
    "required": ["drivers", "guidance"],
}

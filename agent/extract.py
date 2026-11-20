"""Agent step 2: Claude reads the release and copies out the reported figures."""

from agent.config import PROMPTS_DIR
from agent.llm import ask_claude
from agent.schemas import EXTRACTION_TOOL_SCHEMA, METRICS, Extraction

PROMPT_VERSION = "extract_v1"


def wrap_document(release_text: str) -> str:
    """Put the release inside clear markers so Claude treats it as material to read."""
    return f"<document>\n{release_text}\n</document>"


def extract_figures(release_text: str) -> Extraction:
    metric_list = "\n".join(f"- {key}: {info['definition']}" for key, info in METRICS.items())
    system_prompt = (PROMPTS_DIR / f"{PROMPT_VERSION}.md").read_text(encoding="utf-8")
    system_prompt = system_prompt.replace("{metric_list}", metric_list)

    answer = ask_claude(system_prompt, wrap_document(release_text), "record_figures", EXTRACTION_TOOL_SCHEMA)
    return Extraction.model_validate(answer)

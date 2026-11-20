"""Agent step 4: Claude explains each big variance and reads the guidance."""

from agent.config import PROMPTS_DIR
from agent.extract import wrap_document
from agent.llm import ask_claude
from agent.schemas import CLASSIFICATION_TOOL_SCHEMA, METRICS, Classification
from agent.variance import Variance

PROMPT_VERSION = "classify_v2"


def classify_drivers(release_text: str, flagged: list[Variance]) -> Classification:
    if flagged:
        lines = [
            f"- {v.metric} ({METRICS[v.metric]['label']}): came in "
            f"{'above' if v.difference > 0 else 'below'} our estimate"
            for v in flagged
        ]
        variance_list = "\n".join(lines)
    else:
        variance_list = "(none - return an empty drivers list and only report guidance)"

    system_prompt = (PROMPTS_DIR / f"{PROMPT_VERSION}.md").read_text(encoding="utf-8")
    system_prompt = system_prompt.replace("{variance_list}", variance_list)

    answer = ask_claude(system_prompt, wrap_document(release_text), "record_drivers", CLASSIFICATION_TOOL_SCHEMA)
    return Classification.model_validate(answer)

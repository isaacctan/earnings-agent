"""The one place where the program talks to Claude.

Claude is asked to "fill in a form" (the schema) instead of writing free text.
That way the answer always arrives in a shape the code can check.
"""

import anthropic

from agent.config import SetupError, get_anthropic_api_key, get_claude_model


def ask_claude(system_prompt: str, user_message: str, form_name: str, form_schema: dict) -> dict:
    """Send one request to Claude and return the filled-in form as a dictionary."""
    client = anthropic.Anthropic(api_key=get_anthropic_api_key())
    try:
        response = client.messages.create(
            model=get_claude_model(),
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            tools=[
                {
                    "name": form_name,
                    "description": "Record the answer in this exact structure.",
                    "input_schema": form_schema,
                }
            ],
            tool_choice={"type": "tool", "name": form_name},
        )
    except anthropic.AuthenticationError:
        raise SetupError("Claude rejected the API key. Check ANTHROPIC_API_KEY in your .env file.")
    except anthropic.NotFoundError:
        raise SetupError(
            f"Claude does not recognise the model '{get_claude_model()}'. "
            "Check CLAUDE_MODEL in your .env file."
        )
    except anthropic.APIError as error:
        raise SetupError(f"The request to Claude failed: {error}")

    for block in response.content:
        if block.type == "tool_use":
            return block.input
    raise SetupError("Claude answered, but not in the expected structure. Try again.")

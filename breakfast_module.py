
"""RTCFR prompt construction and output validation."""

from langchain_core.messages import HumanMessage, SystemMessage

DEFAULT_RTCFR_PROMPT = """ROLE:
You are a helpful, accurate, and practical assistant.

TASK:
Complete the user's requested task clearly and directly.

CONTEXT:
Adapt your response to the user's topic, audience, constraints, and preferences.
Make reasonable assumptions when information is missing.
Avoid unsupported claims and use appropriate caution for sensitive topics.

FEW-SHOT:
Follow any examples supplied by the user. If no examples are provided,
choose a clear format suitable for the task.

RESPONSE:
Follow the requested output format.
Be organized, relevant, and concise.
Do not force every task into a breakfast or five-item response.
"""


def build_messages(
    user_request: str,
    system_prompt: str = DEFAULT_RTCFR_PROMPT,
    output_instructions: str = "",
):
    """Create explicit LangChain system and human messages."""

    human_content = f"User task:\n{user_request.strip()}"

    if output_instructions.strip():
        human_content += (
            "\n\nOutput format requirements:\n"
            + output_instructions.strip()
        )

    return [
        SystemMessage(content=system_prompt.strip()),
        HumanMessage(content=human_content),
    ]


def validate_output(text: str, output_format: str = "Free-form response"):
    """Perform lightweight output-format validation."""

    content = (text or "").strip()

    if not content:
        return False, "The model returned an empty response."

    if output_format == "Free-form response":
        return True, "Response is non-empty."

    lines = [line.strip() for line in content.splitlines() if line.strip()]

    if output_format == "Numbered list":
        numbered = [
            line for line in lines
            if len(line) > 1
            and line[0].isdigit()
            and line[1] in ".)"
        ]
        return (
            (True, f"Detected {len(numbered)} numbered item(s).")
            if numbered
            else (False, "No numbered items were detected.")
        )

    if output_format == "Markdown table":
        table_lines = [line for line in lines if "|" in line]
        has_separator = any(
            all(
                part.strip().replace(":", "").replace("-", "") == ""
                for part in line.strip("|").split("|")
            )
            for line in table_lines
        )
        valid = len(table_lines) >= 2 and has_separator
        return (
            (True, "Markdown table structure detected.")
            if valid
            else (False, "A clear Markdown table was not detected.")
        )

    if output_format == "Exactly five items":
        if len(lines) != 5:
            return False, f"Expected five lines; received {len(lines)}."

        for number, line in enumerate(lines, start=1):
            if not line.startswith(f"{number}."):
                return False, f"Line {number} should start with '{number}.'"

        return True, "Exactly five numbered lines detected."

    return True, "No additional validation configured."


# Backward compatibility with the original breakfast assignment.
RTCFR_PROMPT = DEFAULT_RTCFR_PROMPT


def build_breakfast_messages(user_request: str):
    return build_messages(
        user_request=user_request,
        system_prompt=DEFAULT_RTCFR_PROMPT,
        output_instructions=(
            "Return exactly five numbered lines, one idea per line."
        ),
    )


def validate_breakfast_output(text: str):
    return validate_output(text, "Exactly five items")

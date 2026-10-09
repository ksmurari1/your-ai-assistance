
"""Basic OpenAI moderation guardrail for user-provided text."""

from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# Categories blocked by this educational demo.
BLOCKED_CATEGORIES = (
    "sexual",
    "sexual/minors",
    "violence",
    "violence/graphic",
    "self-harm",
    "self-harm/intent",
    "self-harm/instructions",
    "hate",
    "hate/threatening",
    "harassment",
    "harassment/threatening",
    "illicit",
    "illicit/violent",
)

# Demonstration thresholds, not official OpenAI safety thresholds.
# Calibrate these values for your application's needs.
CATEGORY_SCORE_THRESHOLDS = {
    "sexual": 0.25,
}


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str
    details: dict[str, Any]


def _to_dict(value):
    """Convert an SDK response object into a dictionary."""
    if hasattr(value, "model_dump"):
        return value.model_dump()

    if isinstance(value, dict):
        return value

    return {}


def _get_category_value(data: dict, category: str):
    """Support category names containing either '/' or '_'."""
    candidates = (
        category,
        category.replace("/", "_"),
    )

    for key in candidates:
        if key in data:
            return data[key]

    return None


def check_text_with_moderation(text: str) -> GuardrailResult:
    """
    Check user input before generation.

    Blocks input when:
    1. The moderation API flags the input.
    2. A configured blocked category is marked true.
    3. A configured category score meets its threshold.
    """
    if not text or not text.strip():
        return GuardrailResult(
            allowed=False,
            reason="Empty input is not allowed.",
            details={"empty_input": True},
        )

    # Reads OPENAI_API_KEY from the environment or loaded .env file.
    client = OpenAI()

    response = client.moderations.create(
        model="omni-moderation-latest",
        input=text,
    )

    payload = _to_dict(response)
    results = payload.get("results", [])

    if not results:
        # Fallback for SDK response objects.
        response_results = getattr(response, "results", [])

        if response_results:
            results = [_to_dict(response_results[0])]

    if not results:
        raise RuntimeError(
            "The moderation API returned no moderation results."
        )

    first = results[0]

    categories = first.get("categories", {}) or {}
    scores = first.get("category_scores", {}) or {}
    api_flagged = bool(first.get("flagged", False))

    flagged_categories = []

    # Check the API's category flags.
    for category in BLOCKED_CATEGORIES:
        category_flag = _get_category_value(categories, category)

        if category_flag is True and category not in flagged_categories:
            flagged_categories.append(category)

    # Apply our additional score-based policy.
    threshold_matches = {}

    for category, threshold in CATEGORY_SCORE_THRESHOLDS.items():
        score = _get_category_value(scores, category)

        if score is None:
            continue

        score = float(score)

        threshold_matches[category] = {
            "score": score,
            "threshold": threshold,
            "blocked": score >= threshold,
        }

        if score >= threshold and category not in flagged_categories:
            flagged_categories.append(category)

    is_flagged = api_flagged or bool(flagged_categories)

    details = {
        "flagged": is_flagged,
        "api_flagged": api_flagged,
        "flagged_categories": flagged_categories,
        "categories": categories,
        "category_scores": scores,
        "threshold_matches": threshold_matches,
    }

    if is_flagged:
        if flagged_categories:
            detail = ", ".join(flagged_categories)
        else:
            detail = "the moderation API flagged the input"

        return GuardrailResult(
            allowed=False,
            reason=(
                "Blocked by the safety guardrail because "
                f"{detail}."
            ),
            details=details,
        )

    return GuardrailResult(
        allowed=True,
        reason=(
            "No configured blocked category or score threshold "
            "was triggered."
        ),
        details=details,
    )


def summarize_moderation(result: GuardrailResult) -> str:
    """Return a concise explanation of the moderation decision."""
    return result.reason

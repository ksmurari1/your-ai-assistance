"""LangChain model setup and general-purpose response generation."""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from breakfast_module import (
    DEFAULT_RTCFR_PROMPT,
    build_messages,
    build_breakfast_messages,
    validate_output,
    validate_breakfast_output,
)

load_dotenv()

MODEL_NAME = "gpt-4o-mini"


def get_client_status():
    return {
        "api_key_configured": bool(os.getenv("OPENAI_API_KEY", "").strip()),
        "model": MODEL_NAME,
    }


def create_chat_model():
    """Create the model only when an API key is available."""
    if not os.getenv("OPENAI_API_KEY", "").strip():
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    return ChatOpenAI(
        model=MODEL_NAME,
        temperature=0,
        max_tokens=700,
        timeout=45,
        max_retries=1,
    )


def generate_response(
    user_request: str,
    system_prompt: str = DEFAULT_RTCFR_PROMPT,
    output_instructions: str = "",
) -> str:
    """Generate a general-purpose response using explicit LangChain messages."""
    messages = build_messages(
        user_request=user_request,
        system_prompt=system_prompt,
        output_instructions=output_instructions,
    )
    response = create_chat_model().invoke(messages)
    content = response.content
    if not isinstance(content, str):
        content = str(content)
    return content.strip()


def generate_breakfast_ideas(user_request: str) -> str:
    """Backward-compatible function for the original breakfast assignment."""
    messages = build_breakfast_messages(user_request)
    response = create_chat_model().invoke(messages)
    content = response.content
    if not isinstance(content, str):
        content = str(content)
    valid, note = validate_breakfast_output(content)
    return content.strip()

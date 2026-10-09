"""Standalone Day 5 assignment script: generate five healthy breakfast ideas."""

import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

SYSTEM_PROMPT = """ROLE:
You are a practical assistant that suggests simple, balanced breakfast ideas.

TASK:
Suggest exactly five healthy breakfast ideas.

CONTEXT:
Interpret healthy as generally balanced, varied, and practical. Do not promise medical benefits.

FEW-SHOT FORMAT EXAMPLE:
1. Oats with plain yogurt, berries, and seeds.
2. Vegetable omelette with whole-grain toast.

RESPONSE:
Return exactly five numbered lines, one idea per line.
Do not include a heading, preamble, conclusion, or extra commentary.
"""

def main():
    if not os.getenv("OPENAI_API_KEY", "").strip():
        raise SystemExit("Please set OPENAI_API_KEY in your terminal before running this script.")

    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=180,
        max_retries=1,
    )
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content="Suggest five healthy breakfast ideas."),
    ]

    # The model returns an AIMessage. Print its text content only.
    reply = model.invoke(messages)
    print(reply.content)

if __name__ == "__main__":
    main()

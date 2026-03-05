from typing import Optional

from google import genai
from google.genai import types

from src.core.config import config


def call_model(
    query: list[str | types.Part],
    model: Optional[str] = config.GEMINI_MODEL,
    system_instruction: Optional[str] = "",
) -> str:
    print(f"  - Calling agent for query (size: {len(query)})...")
    client = genai.Client()

    response = client.models.generate_content(
        model=model,
        contents=query,
        config=types.GenerateContentConfig(system_instruction=system_instruction),
    )

    return response.text

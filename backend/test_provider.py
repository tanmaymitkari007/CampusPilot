
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from ai.factory import generate_with_fallback

prompt = """
Extract actionable tasks from this message:
"Submit the AI assignment by 25 October 2026."

Return JSON with a tasks array. Each task should include
title, deadline, and evidence. Use null if the deadline is unknown.
"""

try:
    result, provider = generate_with_fallback(prompt)
    print("Provider used:", provider)
    print("Response:")
    print(result)
except RuntimeError as exc:
    print("Provider error:", exc)

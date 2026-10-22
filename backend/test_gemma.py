
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Load backend/.env explicitly.
load_dotenv(Path(__file__).with_name(".env"))

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing from backend/.env")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model=model,
    contents=(
        "Extract the task and deadline from this message: "
        "'Submit the AI assignment by 25 October 2026.' "
        "Return the task and deadline in JSON."
    ),
)

print("Model:", model)
print("Response:")
print(response.text)

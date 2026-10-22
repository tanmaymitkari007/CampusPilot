
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from ai.ollama_provider import OllamaProvider

provider = OllamaProvider()

result = provider.generate(
    'Extract the task and deadline from: '
    '"Submit the AI assignment by 25 October 2026." '
    'Return JSON.'
)

print("Provider:", provider.name)
print(result)

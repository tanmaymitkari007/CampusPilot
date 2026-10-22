
import os
import requests

from .base import AIProvider


class OllamaProvider(AIProvider):
    name = "ollama"

    def __init__(self):
        self.base_url = os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        ).rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "gemma4:e2b")

    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()

        result = response.json().get("response", "")
        if not result:
            raise RuntimeError("Ollama returned an empty response")

        return result

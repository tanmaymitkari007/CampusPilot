
import os
from pathlib import Path

from dotenv import load_dotenv

from .base import AIProvider
from .gemma_provider import GemmaProvider
from .ollama_provider import OllamaProvider


# Always load the backend configuration, regardless of the
# directory from which Uvicorn or a test is launched.
BACKEND_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(BACKEND_ENV, override=False)


def create_provider(name: str) -> AIProvider:
    if name == "gemma":
        return GemmaProvider()

    if name == "ollama":
        return OllamaProvider()

    raise ValueError(f"Unsupported AI provider: {name}")


def get_provider() -> AIProvider:
    name = os.getenv("AI_PROVIDER", "gemma").strip().lower()
    return create_provider(name)


def generate_with_fallback(prompt: str) -> tuple[str, str]:
    primary = os.getenv("AI_PROVIDER", "gemma").strip().lower()
    fallback_enabled = (
        os.getenv("AI_FALLBACK_ENABLED", "true").strip().lower()
        == "true"
    )

    if primary not in {"gemma", "ollama"}:
        raise ValueError(f"Unsupported AI_PROVIDER: {primary}")

    provider_order = [primary]

    if fallback_enabled:
        provider_order.append(
            "ollama" if primary == "gemma" else "gemma"
        )

    errors = []

    for provider_name in provider_order:
        try:
            provider = create_provider(provider_name)
            result = provider.generate(prompt)
            return result, provider.name
        except Exception as exc:
            # Keep trying the next configured provider.
            errors.append(f"{provider_name}: {type(exc).__name__}: {exc}")

    raise RuntimeError(
        "All configured AI providers failed: " + " | ".join(errors)
    )

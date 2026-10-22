from abc import ABC, abstractmethod


class AIProvider(ABC):
    name: str

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Return the model's text response."""
        raise NotImplementedError

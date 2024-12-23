from enum import Enum


class LLMOption(Enum):
    OPENAI = "OpenAI"
    ANTHROPIC = "Anthropic"
    GEMINI = "Gemini"
    OLLAMA = "Ollama"

    @classmethod
    def list_options(cls):
        return [{"name": option.value, "value": option.name} for option in cls]

    @classmethod
    def from_name(cls, name):
        try:
            return cls[name]
        except KeyError:
            return None

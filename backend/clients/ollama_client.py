import logging
import os

from ollama import Client


class OllamaClient:
    def __init__(
        self,
        host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        model: str = os.getenv("OLLAMA_MODEL", "gemma2:latest"),
    ):
        self.host = host
        self.model = model
        self.client = Client(host=host)

    def list_models(self) -> list[str]:
        try:
            response = self.client.list()
            return [m.model for m in response.models]
        except Exception as e:
            logging.error(f"Error listing Ollama models: {e}")
            return []

    def chat(self, prompt):
        try:
            answer = self.client.generate(model=self.model, prompt=prompt)
            return answer.response
        except Exception as e:
            logging.error(f"Error communicating with Ollama API: {e}")
            return None

    def chat_with_history(self, system: str, messages: list[dict]) -> str:
        full_messages = [{"role": "system", "content": system}] + messages
        try:
            response = self.client.chat(model=self.model, messages=full_messages)
            return response.message.content
        except Exception as e:
            logging.error(f"Error communicating with Ollama API: {e}")
            return None

import logging

from ollama import Client


class OllamaClient:
    def __init__(self, host="http://localhost:11434", model="gemma2:latest"):
        self.host = host
        self.model = model
        self.client = Client(host=host)

    def chat(self, prompt):
        try:
            answer = self.client.generate(model=self.model, prompt=prompt)
            return answer.response
        except Exception as e:
            logging.error(f"Error communicating with Ollama API: {e}")
            return None

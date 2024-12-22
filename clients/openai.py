import os

import requests
from dotenv import load_dotenv

load_dotenv()


class OpenAIClient:
    def __init__(self, host="https://api.openai.com/v1/chat/completions", model="gpt-4o-mini"):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.host = host
        self.model = model
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def chat(self, user_prompt):
        messages = [
            {"role": "user", "content": user_prompt},
        ]
        payload = {
            "model": self.model,
            "messages": messages,
        }
        try:
            response = requests.post(self.host, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with OpenAI API: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing OpenAI API response: {e}")
            return None

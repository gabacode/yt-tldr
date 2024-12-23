import os

import requests
from dotenv import load_dotenv

load_dotenv()


class AnthropicClient:
    def __init__(self, host="https://api.anthropic.com/v1/messages", model="claude-3-5-sonnet-20241022"):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.host = host
        self.model = model
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

    def chat(self, user_prompt, max_tokens=1024):
        messages = [
            {"role": "user", "content": user_prompt},
        ]
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        try:
            response = requests.post(self.host, headers=self.headers, json=payload)
            response.raise_for_status()
            answer = response.json()
            return answer["content"][0]["text"].strip()
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Anthropic API: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing Anthropic API response: {e}")
            return None

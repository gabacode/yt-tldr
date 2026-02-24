import os

import requests
from dotenv import load_dotenv

load_dotenv()


_GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiClient:
    def __init__(self, model: str = "gemini-1.5-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = model
        self.host = f"{_GEMINI_BASE}/{model}:generateContent"
        self.headers = {
            "Content-Type": "application/json",
        }

    def chat(self, user_prompt):
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": user_prompt}
                    ]
                }
            ]
        }
        try:
            url = f"{self.host}?key={self.api_key}"
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            answer = response.json()
            return answer["candidates"][0]["content"]["parts"][0]["text"].strip()
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Gemini API: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing Gemini API response: {e}")
            return None

    def chat_with_history(self, system: str, messages: list[dict]) -> str:
        contents = [
            {"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
            for m in messages
        ]
        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": contents,
        }
        try:
            url = f"{self.host}?key={self.api_key}"
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Gemini API: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing Gemini API response: {e}")
            return None

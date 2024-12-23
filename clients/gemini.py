import os

import requests
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    def __init__(self, host="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.host = host
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

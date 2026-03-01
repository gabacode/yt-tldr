import logging
import os
import re

import requests


class TranscriptProcessor:
    """
    Handles transcript cleaning, conversion from VTT to text, and related tasks.
    """

    @staticmethod
    def clean_transcript(raw_transcript):
        """
        Cleans the raw transcript by removing timecodes, tags, filler words,
        duplicate phrases, and normalizing whitespace.
        """
        # Step 1: Remove timecodes like <00:00:01.079>
        cleaned = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', raw_transcript)

        # Step 2: Remove tags like <c> and </c>
        cleaned = re.sub(r'</?c>', '', cleaned)

        # Step 3: Remove filler words (optional)
        filler_words = ['um', 'uh', 'like', 'you know', 'so', 'actually']
        pattern = r'\b(?:' + '|'.join(filler_words) + r')\b'
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        # Step 4: Remove duplicate consecutive words (simple approach)
        cleaned = re.sub(r'\b(\w+)( \1\b)+', r'\1', cleaned, flags=re.IGNORECASE)

        # Step 5: Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

    @staticmethod
    def vtt_to_text(vtt_file):
        """
        Convert a WebVTT subtitle file to a clean transcript text.
        """
        lines = []
        with open(vtt_file, 'r', encoding='utf-8') as f:
            for line in f:
                if '-->' in line or line.strip() == "" or line.strip().startswith("WEBVTT"):
                    continue
                clean_line = re.sub(r'</?c>', '', line)
                lines.append(clean_line.strip())

        raw_transcript = " ".join(lines)
        return TranscriptProcessor.clean_transcript(raw_transcript)


class Transcriber:
    def __init__(self, model_name: str = "turbo"):
        self.model_name = model_name
        self.whisper_url = os.getenv("WHISPER_URL", "http://whisper_service:9000")

    def transcribe_with_whisper(self, audio_file: str) -> str | None:
        try:
            with open(audio_file, "rb") as f:
                response = requests.post(
                    f"{self.whisper_url}/transcribe",
                    files={"file": f},
                    data={"model": self.model_name},
                    timeout=300,
                )
            response.raise_for_status()
            return response.json()["transcript"]
        except Exception as e:
            logging.error("Error calling Whisper service: %s", e)
            return None

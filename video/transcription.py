import logging
import os
import re
import warnings

import whisper
from rich.console import Console

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
warnings.filterwarnings("ignore", category=FutureWarning)

console = Console()


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
    def __init__(self, model_name):
        self.model_name = model_name
        try:
            self.model = whisper.load_model(self.model_name)
        except Exception as e:
            logging.error("Error loading Whisper model '%s': %s", self.model_name, e)
            self.model = None

    def transcribe_with_whisper(self, audio_file):
        if self.model is None:
            logging.error("No model loaded; cannot transcribe.")
            return None

        try:
            audio = whisper.load_audio(audio_file)
            snippet = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(snippet, n_mels=self.model.dims.n_mels).to(self.model.device)
            _, probs = self.model.detect_language(mel)
            detected_language = max(probs, key=probs.get)
            console.print(f"[bold cyan]\nDetected language: {detected_language}[/bold cyan]")
        except Exception as e:
            logging.error("Error detecting language: %s", e)
            return None

        try:
            result = self.model.transcribe(audio_file)
            raw_transcript = result["text"]
        except Exception as e:
            logging.error("Error during transcription: %s", e)
            return None

        try:
            return TranscriptProcessor.clean_transcript(raw_transcript)
        except Exception as e:
            logging.error("Error cleaning transcript: %s", e)
            return None

import logging
import re
import subprocess
from pathlib import Path


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
    """
    Uses Whisper CLI to transcribe audio files.
    """

    def __init__(self, model="medium"):
        self.model = model

    def transcribe_with_whisper(self, audio_file):
        """
        Use local Whisper CLI to transcribe the audio file.
        Returns the transcript text or None on error.
        """
        cmd_whisper = ["whisper", audio_file, "--model", self.model, "--language", "en"]
        result = subprocess.run(cmd_whisper, capture_output=True, text=True)
        if result.returncode != 0:
            logging.debug("Whisper transcription error: %s", result.stderr)
            return None

        transcript_file = Path(audio_file).with_suffix(".txt")
        if transcript_file.exists():
            raw_transcript = transcript_file.read_text(encoding='utf-8')
            return TranscriptProcessor.clean_transcript(raw_transcript)
        return None

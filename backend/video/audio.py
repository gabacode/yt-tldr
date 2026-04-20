import logging
import subprocess
from pathlib import Path


class AudioDownloader:
    """
    Downloads the best audio track from a YouTube video using yt-dlp.
    """

    def __init__(self, url, output_dir):
        self.url = url
        self.output_dir = Path(output_dir)

    def download_audio(self):
        """
        Download the best audio track for transcription with Whisper.
        Returns the path to the downloaded audio file or None on error.
        """
        audio_path = self.output_dir / "audio.m4a"
        cmd = [
            "yt-dlp",
            "--newline",
            "-f", "bestaudio/worst",
            "-o", str(audio_path),
            self.url,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logging.error("yt-dlp failed (code %d):\n%s", result.returncode, result.stderr or result.stdout)
            return None

        return audio_path.as_posix()

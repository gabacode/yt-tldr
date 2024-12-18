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
        cmd_download_audio = [
            "yt-dlp",
            "-f", "bestaudio",
            "-o", str(audio_path),
            self.url
        ]
        result = subprocess.run(cmd_download_audio, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error("Error downloading audio: %s", result.stderr)
            return None
        return audio_path.as_posix()

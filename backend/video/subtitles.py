import logging
import subprocess
from pathlib import Path


class SubtitleManager:
    """
    Manages subtitle checking and downloading from YouTube videos using yt-dlp.
    """

    def __init__(self, url, output_dir):
        self.url = url
        self.output_dir = Path(output_dir)

    def check_and_download_subtitles(self):
        """
        Check if subtitles are available and download them if so.
        Returns the path to the subtitle file if found, otherwise None.
        """
        # Check available subtitles
        cmd_list_subs = ["yt-dlp", "--list-subs", self.url]
        result = subprocess.run(cmd_list_subs, capture_output=True, text=True)

        if result.returncode != 0:
            logging.error("Error checking subtitles: %s", result.stderr)
            return None

        # Look for English subtitles in the output.
        has_subtitles = any('en' in line.lower() for line in result.stdout.splitlines())

        if not has_subtitles:
            return None

        # Download the English auto-subtitles
        cmd_download_subs = [
            "yt-dlp",
            "--skip-download",
            "--write-auto-sub",
            "--sub-lang", "en",
            "--convert-subs", "vtt",
            "-o", str(self.output_dir / "%(title)s.%(ext)s"),
            self.url
        ]
        result = subprocess.run(cmd_download_subs, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error("Error downloading subtitles: %s", result.stderr)
            return None

        # Find the downloaded .vtt file
        vtt_files = list(self.output_dir.glob("*.en.vtt"))
        if vtt_files:
            return vtt_files[0].as_posix()
        return None

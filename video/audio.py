import logging
import subprocess
from pathlib import Path

from rich.console import Console
from rich.progress import Progress

console = Console()


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
            "--newline",
            "-f", "bestaudio",
            "-o", str(audio_path),
            self.url
        ]

        with subprocess.Popen(cmd_download_audio, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                              bufsize=1) as proc:
            if proc.stdout is None:
                logging.error("No stdout available from yt-dlp.")
                return None

            with Progress(transient=True) as progress:
                task_id = progress.add_task("Downloading audio", total=100)
                for line in proc.stdout:
                    if "[download]" in line:
                        parts = line.strip().split()
                        for p in parts:
                            if p.endswith("%"):
                                try:
                                    percent = float(p.replace("%", ""))
                                    progress.update(task_id, completed=percent)
                                except ValueError:
                                    pass

            return_code = proc.wait()

        if return_code != 0:
            logging.error("Error downloading audio. yt-dlp returned code %d", return_code)
            return None

        return audio_path.as_posix()

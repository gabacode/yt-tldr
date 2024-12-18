import json
import logging
import subprocess


class VideoInfoRetriever:
    """
    Retrieves metadata about a YouTube video using yt-dlp,
    including its duration in seconds.
    """

    def __init__(self, url):
        self.url = url

    def get_video_length_seconds(self):
        """
        Uses yt-dlp to get video metadata in JSON and extracts duration.
        Returns the duration in seconds or None if not found.
        """
        cmd = ["yt-dlp", "--dump-single-json", self.url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error("Error retrieving video info: %s", result.stderr)
            return None

        try:
            info = json.loads(result.stdout)
            duration = info.get("duration")
            return duration
        except json.JSONDecodeError:
            logging.error("Failed to parse video info JSON.")
            return None

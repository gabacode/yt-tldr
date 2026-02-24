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

    def get_video_info(self):
        """
        Uses yt-dlp to get video metadata in JSON and extracts its details.
        """
        cmd = ["yt-dlp", "--dump-single-json", self.url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error("Error retrieving video info: %s", result.stderr)
            return None
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            logging.error("Failed to parse video info JSON.")
            return None

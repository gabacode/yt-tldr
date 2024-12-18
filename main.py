import logging
import re
import sys

from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

from summary.summarizer import YouTubeSummarizer

logging.basicConfig(level=logging.INFO)
console = Console()

YOUTUBE_URL_PATTERN = r"^(https?://(www\.)?youtube\.com/watch\?v=[\w-]+)$"


def validate_youtube_url(url: str) -> bool:
    """
    Basic validation to check if the URL matches a YouTube watch link.
    """
    return bool(re.match(YOUTUBE_URL_PATTERN, url))


def get_youtube_url_from_user() -> str:
    """
    Prompt the user repeatedly until a valid YouTube URL is entered.
    """
    while True:
        console.print(
            "Please enter a valid YouTube URL (e.g. [bold]https://www.youtube.com/watch?v=kpTxAIPcEAY[/bold]):",
            style="cyan")
        url = Prompt.ask("YouTube URL")
        if validate_youtube_url(url):
            return url
        else:
            console.print(Text("The provided URL is not a valid YouTube watch link. Please try again.", style="red"))


def main():
    # If a command-line argument is provided, use it. Otherwise, prompt the user.
    if len(sys.argv) > 1:
        youtube_url = sys.argv[1]
        if not validate_youtube_url(youtube_url):
            console.print(Text("Error: The provided command-line URL is not valid.", style="red"))
            console.print(
                Text("Please run the script again with a valid URL or omit the parameter to be prompted for one.",
                     style="yellow"))
            sys.exit(1)
    else:
        youtube_url = get_youtube_url_from_user()

    summarizer = YouTubeSummarizer(youtube_url)
    summarizer.run()


if __name__ == "__main__":
    main()

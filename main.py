import logging
import re
import sys

from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

from models.llm_option import LLMOption
from summary.summarizer import YouTubeSummarizer

logging.basicConfig(level=logging.INFO)
console = Console()


def validate_youtube_url(url: str) -> bool:
    """
    Basic validation to check if the URL matches a YouTube watch link.
    """
    pattern = r"^(https?://(www\.)?youtube\.com/watch\?v=[\w-]+)$"
    return bool(re.match(pattern, url))


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


def select_llm() -> LLMOption:
    options = LLMOption.list_options()
    console.print("Please select the language model you want to use:")
    for idx, option in enumerate(options, start=1):
        console.print(f"[cyan]{idx}[/cyan]: {option['name']}")
    llm_value = Prompt.ask("Select language model (1/2/3)", default="3")
    try:
        llm_index = int(llm_value) - 1
        if 0 <= llm_index < len(options):
            return LLMOption.from_name(options[llm_index]["value"])
    except (ValueError, IndexError):
        pass
    console.print(Text("Invalid selection. Please try again.", style="red"))


def get_youtube_url_from_params():
    """
    Get the YouTube URL from the command-line parameters.
    """
    youtube_url = sys.argv[1]
    if not validate_youtube_url(youtube_url):
        console.print(Text("Error: The provided command-line URL is not valid.", style="red"))
        console.print(
            Text("Please run the script again with a valid URL or omit the parameter to be prompted for one.",
                 style="yellow"))
        sys.exit(1)
    return youtube_url


def main():
    youtube_url = get_youtube_url_from_params() if len(sys.argv) > 1 else get_youtube_url_from_user()
    llm = select_llm()
    summarizer = YouTubeSummarizer(youtube_url, llm)
    summarizer.run()


if __name__ == "__main__":
    main()

import logging
import os
import re
import sys

import requests
from dotenv import load_dotenv

load_dotenv()
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

logging.basicConfig(level=logging.INFO)
console = Console()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def fetch_llm_options() -> list[dict]:
    try:
        response = requests.get(f"{API_BASE_URL}/llms", timeout=5)
        response.raise_for_status()
        return response.json()["llms"]
    except requests.exceptions.ConnectionError:
        console.print(Text(f"Error: Could not connect to the API at {API_BASE_URL}. Is the server running?", style="red"))
        sys.exit(1)


def validate_youtube_url(url: str) -> bool:
    pattern = r"^(https?://(www\.)?youtube\.com/watch\?v=[\w-]+)$"
    return bool(re.match(pattern, url))


def get_youtube_url_from_user() -> str:
    while True:
        console.print(
            "Please enter a valid YouTube URL (e.g. [bold]https://www.youtube.com/watch?v=kpTxAIPcEAY[/bold]):",
            style="cyan")
        url = Prompt.ask("YouTube URL")
        if validate_youtube_url(url):
            return url
        else:
            console.print(Text("The provided URL is not a valid YouTube watch link. Please try again.", style="red"))


def select_llm() -> str:
    options = fetch_llm_options()
    console.print("Please select the language model you want to use:")
    for idx, option in enumerate(options, start=1):
        console.print(f"[cyan]{idx}[/cyan]: {option['name']}")
    llm_value = Prompt.ask(
        f"Select language model ({'/'.join(str(i) for i in range(1, len(options) + 1))})",
        default="4"
    )
    try:
        llm_index = int(llm_value) - 1
        if 0 <= llm_index < len(options):
            return options[llm_index]["value"]
    except (ValueError, IndexError):
        pass
    console.print(Text("Invalid selection. Please try again.", style="red"))


def get_youtube_url_from_params():
    youtube_url = sys.argv[1]
    if not validate_youtube_url(youtube_url):
        console.print(Text("Error: The provided command-line URL is not valid.", style="red"))
        console.print(
            Text("Please run the script again with a valid URL or omit the parameter to be prompted for one.",
                 style="yellow"))
        sys.exit(1)
    return youtube_url


def select_language() -> str:
    language = Prompt.ask("Please enter the language you want to summarize the video in (e.g. English):",
                          default="English")
    return language.strip().lower()


def call_summarize_api(url: str, llm: str, language: str) -> dict:
    payload = {"url": url, "llm": llm, "language": language}
    response = requests.post(f"{API_BASE_URL}/summarize", json=payload, timeout=600)
    response.raise_for_status()
    return response.json()


def display_summary(result: dict):
    video_title = result["video_title"]
    summary = result["summary"]
    console.print(Panel(Markdown(f"## {video_title}\n\n{summary}"),
                        title="[bold green]Video Summary[/bold green]",
                        border_style="green"))


def display_time_stats(result: dict):
    stats = result["time_stats"]
    video_length_seconds = stats["video_length_seconds"]
    video_length_minutes = stats["video_length_minutes"]
    reading_time_seconds = stats["reading_time_seconds"]
    reading_time_minutes = stats["reading_time_minutes"]
    time_saved_minutes = stats["time_saved_minutes"]
    time_saved_seconds = stats["time_saved_seconds"]
    percentage_saved = stats["percentage_saved"]

    def format_time(minutes, seconds):
        if minutes < 1:
            return f"{int(seconds)} seconds"
        return f"{minutes:.2f} minutes"

    video_time_str = format_time(video_length_minutes, video_length_seconds)
    reading_time_str = format_time(reading_time_minutes, reading_time_seconds)

    table = Table(box=box.ROUNDED, expand=True, title="Time Comparison")
    table.add_column("Metric", style="bold cyan")
    table.add_column("Time", justify="right", style="bold magenta")

    table.add_row("Video length", video_time_str)
    table.add_row("Reading time", reading_time_str)
    table.add_row("Time saved",
                  f"{time_saved_minutes:.2f} min ({int(time_saved_seconds)} s) ≈ {percentage_saved:.0f}%")

    console.print(table)

    if video_length_minutes > 0:
        reading_proportion = reading_time_minutes / video_length_minutes
    else:
        reading_proportion = 0

    console.print("[bold blue]\nComparison Bar:[/bold blue]")
    bar_length = 50
    reading_bar = int(bar_length * reading_proportion)
    video_bar_line = "[bold green]Video:   [/bold green]" + "#" * bar_length + f" ({video_time_str})"
    reading_bar_line = "[bold yellow]Reading: [/bold yellow]" + "#" * reading_bar + "-" * (
            bar_length - reading_bar) + f" ({reading_time_str})"

    console.print(video_bar_line)
    console.print(reading_bar_line)
    console.print("\n[green]You saved a lot of time![/green]")


def main():
    youtube_url = get_youtube_url_from_params() if len(sys.argv) > 1 else get_youtube_url_from_user()
    llm = select_llm()
    language = select_language()

    console.print("[bold cyan]\nCalling summarizer API...[/bold cyan]")
    try:
        result = call_summarize_api(youtube_url, llm, language)
    except requests.exceptions.ConnectionError:
        console.print(Text(f"Error: Could not connect to the API at {API_BASE_URL}. Is the server running?",
                           style="red"))
        sys.exit(1)
    except requests.exceptions.HTTPError as exc:
        detail = exc.response.json().get("detail", str(exc))
        console.print(Text(f"Error: {detail}", style="red"))
        sys.exit(1)

    display_summary(result)
    display_time_stats(result)


if __name__ == "__main__":
    main()

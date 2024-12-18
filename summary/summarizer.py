import logging
import tempfile

from ollama import Client
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from video.audio import AudioDownloader
from video.info import VideoInfoRetriever
from video.subtitles import SubtitleManager
from video.transcription import TranscriptProcessor, Transcriber

console = Console()


class Summarizer:
    """
    Uses the Ollama Python client to summarize transcripts.
    """

    def __init__(self, model="gemma2:latest", host='http://localhost:11434'):
        self.model = model
        self.client = Client(host=host, headers={'x-some-header': 'some-value'})

    def summarize_with_ollama(self, transcript,
                              prompt_template="Summarize the following transcript:\n\n{transcript}\n\nSummary:"):
        """
        Summarize the given transcript using Ollama.
        """
        prompt = prompt_template.format(transcript=transcript)
        answer = self.client.generate(model=self.model, prompt=prompt)
        return answer.response


class YouTubeSummarizer:
    """
    Main orchestrator class that:
    - Retrieves video info (length)
    - Attempts to get subtitles, else downloads audio and transcribes
    - Summarizes transcript
    - Calculates time saved
    """

    def __init__(self, youtube_url):
        self.youtube_url = youtube_url
        self.video_length_seconds = None
        self.transcript = None
        self.summary = None

    def run(self):
        # Create a temporary working directory
        with tempfile.TemporaryDirectory() as tmpdir:
            console.print("[bold cyan]\nFetching video information...[/bold cyan]")
            # Get video length
            info = VideoInfoRetriever(self.youtube_url)
            self.video_length_seconds = info.get_video_length_seconds()

            console.print("[bold cyan]\nChecking for subtitles...[/bold cyan]")
            # Try to get subtitles
            subtitle_manager = SubtitleManager(self.youtube_url, tmpdir)
            subtitle_file = subtitle_manager.check_and_download_subtitles()

            if subtitle_file:
                console.print("[green]Subtitles found! Extracting text...[/green]")
                self.transcript = TranscriptProcessor.vtt_to_text(subtitle_file)
            else:
                console.print("[yellow]No subtitles found. Downloading audio and transcribing...[/yellow]")
                audio_downloader = AudioDownloader(self.youtube_url, tmpdir)
                audio_file = audio_downloader.download_audio()
                if not audio_file:
                    logging.error("Failed to download audio.")
                    console.print("[red]Error: Failed to download audio.[/red]")
                    return

                transcriber = Transcriber(model="medium")
                self.transcript = transcriber.transcribe_with_whisper(audio_file)
                if not self.transcript:
                    logging.error("Failed to transcribe audio.")
                    console.print("[red]Error: Failed to transcribe audio.[/red]")
                    return

            logging.debug("Transcript: %s", self.transcript)

            console.print("[bold cyan]\nSummarizing transcript with Ollama...[/bold cyan]")
            summarizer = Summarizer()
            self.summary = summarizer.summarize_with_ollama(self.transcript)

            if self.summary:
                console.print(Panel(Markdown("## Summary\n\n" + self.summary),
                                    title="[bold green]Video Summary[/bold green]",
                                    border_style="green"))
                self.calculate_time_saved()
            else:
                logging.error("Failed to summarize.")
                console.print("[red]Error: Failed to summarize the transcript.[/red]")

    def calculate_time_saved(self):
        """
        Calculates and prints how much time is saved by reading the summary
        instead of watching the entire video. Also shows a styled comparison.

        Assumes:
        - Average reading speed: ~200 words/minute.
        """
        if not self.video_length_seconds:
            console.print("[yellow]No video length info available to calculate time saved.[/yellow]")
            return

        video_length_minutes = self.video_length_seconds / 60.0
        video_length_seconds = self.video_length_seconds
        word_count = len(self.summary.split())
        reading_speed_wpm = 200
        reading_time_minutes = word_count / reading_speed_wpm
        reading_time_seconds = reading_time_minutes * 60

        def format_time(minutes, seconds):
            if minutes < 1:
                return f"{int(seconds)} seconds"
            return f"{minutes:.2f} minutes"

        video_time_str = format_time(video_length_minutes, video_length_seconds)
        reading_time_str = format_time(reading_time_minutes, reading_time_seconds)

        time_saved_minutes = video_length_minutes - reading_time_minutes
        time_saved_seconds = max(0, time_saved_minutes * 60)

        # Calculate percentage
        if video_length_minutes > 0:
            percentage_saved = (time_saved_minutes / video_length_minutes) * 100
        else:
            percentage_saved = 0

        # Create a table for time comparison
        table = Table(box=box.ROUNDED, expand=True, title="Time Comparison")
        table.add_column("Metric", style="bold cyan")
        table.add_column("Time", justify="right", style="bold magenta")

        table.add_row("Video length", video_time_str)
        table.add_row("Reading time", reading_time_str)
        table.add_row("Time saved",
                      f"{time_saved_minutes:.2f} min ({int(time_saved_seconds)} s) ≈ {percentage_saved:.0f}%")

        console.print(table)

        # Show a progress-like bar comparing reading to video
        if video_length_minutes > 0:
            reading_proportion = reading_time_minutes / video_length_minutes
        else:
            reading_proportion = 0

        # Using rich progress bar for a quick comparison:
        console.print("[bold blue]\nComparison Bar:[/bold blue]")
        bar_length = 50
        reading_bar = int(bar_length * reading_proportion)
        video_bar_line = "[bold green]Video:   [/bold green]" + "#" * bar_length + f" ({video_time_str})"
        reading_bar_line = "[bold yellow]Reading: [/bold yellow]" + "#" * reading_bar + "-" * (
                bar_length - reading_bar) + f" ({reading_time_str})"

        console.print(video_bar_line)
        console.print(reading_bar_line)
        console.print("\n[green]You saved a lot of time![/green]")

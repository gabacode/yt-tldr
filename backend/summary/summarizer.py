import logging
import tempfile
from dataclasses import dataclass

from clients import OllamaClient, OpenAIClient, AnthropicClient, GeminiClient
from models import LLMOption
from video.audio import AudioDownloader
from video.info import VideoInfoRetriever
from video.subtitles import SubtitleManager
from video.transcription import TranscriptProcessor, Transcriber


@dataclass
class TimeStats:
    video_length_seconds: float
    video_length_minutes: float
    word_count: int
    reading_time_seconds: float
    reading_time_minutes: float
    time_saved_seconds: float
    time_saved_minutes: float
    percentage_saved: float


@dataclass
class SummaryResult:
    video_title: str
    video_url: str
    llm_used: str
    language: str
    transcript: str
    summary: str
    time_stats: TimeStats


class Summarizer:
    def __init__(self, llm_option: LLMOption, language: str, model: str | None = None):
        self.llm_option = llm_option
        self.client = self.get_client(llm_option, model)
        self.llm_name = self.get_llm_name()
        self.language = language

    @staticmethod
    def get_client(llm_option: LLMOption, model: str | None = None):
        if llm_option == LLMOption.OPENAI:
            return OpenAIClient(model=model) if model else OpenAIClient()
        elif llm_option == LLMOption.ANTHROPIC:
            return AnthropicClient(model=model) if model else AnthropicClient()
        elif llm_option == LLMOption.GEMINI:
            return GeminiClient(model=model) if model else GeminiClient()
        elif llm_option == LLMOption.OLLAMA:
            return OllamaClient(model=model) if model else OllamaClient()
        else:
            raise ValueError(f"Invalid LLM client: {llm_option}")

    def get_llm_name(self):
        return self.llm_option.value

    def summarize(self, title, transcript):
        prompt_template = f"""
        Please summarize the following transcript of the video named '{title}' and provide the summary in {self.language}:

        Transcript:
        {transcript}

        Summary (in {self.language}):
        """
        prompt = prompt_template.format(transcript=transcript)
        return self.client.chat(prompt)


class YouTubeSummarizer:
    """
    Main orchestrator class that:
    - Retrieves video info (length)
    - Attempts to get subtitles, else downloads audio and transcribes
    - Summarizes transcript
    - Calculates time saved
    """

    READING_SPEED_WPM = 200

    def __init__(self, youtube_url: str, llm: LLMOption, language: str, model: str | None = None):
        self.youtube_url = youtube_url
        self.summarizer = Summarizer(llm_option=llm, language=language, model=model)

    def run(self) -> SummaryResult:
        with tempfile.TemporaryDirectory() as tmpdir:
            logging.info("[1/4] Fetching video info for %s", self.youtube_url)
            info = VideoInfoRetriever(self.youtube_url)
            video_info = info.get_video_info()
            video_length_seconds = video_info.get("duration", 0)
            video_title = video_info.get("title", "Unknown")
            logging.info("[1/4] Video: '%s' (%.0fs)", video_title, video_length_seconds)

            logging.info("[2/4] Checking for subtitles...")
            subtitle_manager = SubtitleManager(self.youtube_url, tmpdir)
            subtitle_file = subtitle_manager.check_and_download_subtitles()

            if subtitle_file:
                logging.info("[2/4] Subtitles found, extracting text")
                transcript = TranscriptProcessor.vtt_to_text(subtitle_file)
            else:
                logging.info("[2/4] No subtitles, downloading audio...")
                audio_downloader = AudioDownloader(self.youtube_url, tmpdir)
                audio_file = audio_downloader.download_audio()
                if not audio_file:
                    raise RuntimeError("Failed to download audio.")
                logging.info("[2/4] Audio downloaded, transcribing with Whisper...")
                transcriber = Transcriber(model_name="turbo")
                transcript = transcriber.transcribe_with_whisper(audio_file)
                if not transcript:
                    raise RuntimeError("Failed to transcribe audio.")

            logging.info("[3/4] Transcript ready (%d words), sending to %s...",
                         len(transcript.split()), self.summarizer.llm_name)

            summary = self.summarizer.summarize(video_title, transcript)
            if not summary:
                raise RuntimeError("Failed to summarize the transcript.")

            logging.info("[4/4] Summary received (%d words), building result", len(summary.split()))
            return self._build_result(
                video_title=video_title,
                video_length_seconds=video_length_seconds,
                transcript=transcript,
                summary=summary,
            )

    def _build_result(self, video_title: str, video_length_seconds: float,
                      transcript: str, summary: str) -> SummaryResult:
        video_length_minutes = video_length_seconds / 60.0
        word_count = len(summary.split())
        reading_time_minutes = word_count / self.READING_SPEED_WPM
        reading_time_seconds = reading_time_minutes * 60
        time_saved_minutes = video_length_minutes - reading_time_minutes
        time_saved_seconds = max(0.0, time_saved_minutes * 60)
        percentage_saved = (
            (time_saved_minutes / video_length_minutes) * 100
            if video_length_minutes > 0 else 0.0
        )

        time_stats = TimeStats(
            video_length_seconds=video_length_seconds,
            video_length_minutes=round(video_length_minutes, 2),
            word_count=word_count,
            reading_time_seconds=round(reading_time_seconds, 1),
            reading_time_minutes=round(reading_time_minutes, 2),
            time_saved_seconds=round(time_saved_seconds, 1),
            time_saved_minutes=round(time_saved_minutes, 2),
            percentage_saved=round(percentage_saved, 1),
        )

        return SummaryResult(
            video_title=video_title,
            video_url=self.youtube_url,
            llm_used=self.summarizer.llm_name,
            language=self.summarizer.language,
            transcript=transcript,
            summary=summary,
            time_stats=time_stats,
        )

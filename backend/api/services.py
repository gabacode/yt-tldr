import logging
import re
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException

from api.schemas import ChatMessage, ChatResponse, LLMOption, LLMsResponse, ModelsResponse, SummarizeResponse, TimeStatsResponse
from clients import OllamaClient
from models.llm_option import LLMOption as LLMOptionEnum
from summary.retrieval import retrieve_relevant_chunks
from summary.summarizer import Summarizer, YouTubeSummarizer

_YOUTUBE_URL_RE = re.compile(r"^(https?://(www\.)?youtube\.com/watch\?v=[\w-]+)$")


_STATIC_MODELS: dict[str, list[str]] = {
    "OPENAI": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    "ANTHROPIC": ["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"],
    "GEMINI": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
}


def get_models(llm_value: str) -> ModelsResponse:
    llm = LLMOptionEnum.from_name(llm_value.upper())
    if llm is None:
        raise HTTPException(status_code=422, detail="Unknown LLM.")
    if llm == LLMOptionEnum.OLLAMA:
        models = OllamaClient().list_models()
    else:
        models = _STATIC_MODELS.get(llm_value.upper(), [])
    return ModelsResponse(models=sorted(models))


def get_llms() -> LLMsResponse:
    options = LLMOptionEnum.list_options()
    return LLMsResponse(llms=[LLMOption(name=o["name"], value=o["value"]) for o in options])


def _normalize_youtube_url(url: str) -> str:
    parsed = urlparse(url)
    # Standard watch URL: youtube.com/watch?v=<id>
    video_id = parse_qs(parsed.query).get("v", [None])[0]
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    # Shorts URL: youtube.com/shorts/<id>
    if parsed.path.startswith("/shorts/"):
        video_id = parsed.path.split("/shorts/")[1].split("/")[0]
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
    # Short link: youtu.be/<id>
    if parsed.netloc == "youtu.be":
        video_id = parsed.path.lstrip("/").split("/")[0]
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
    return url


def run_summarize(url: str, llm_value: str, language: str, model: str | None = None) -> SummarizeResponse:
    url = _normalize_youtube_url(url)
    logging.info("Summarize request received — url=%s llm=%s language=%s", url, llm_value, language)

    if not _YOUTUBE_URL_RE.match(url):
        raise HTTPException(status_code=422, detail="Invalid YouTube URL.")

    llm = LLMOptionEnum.from_name(llm_value.upper())
    if llm is None:
        valid = [o["value"] for o in LLMOptionEnum.list_options()]
        raise HTTPException(status_code=422, detail=f"Unknown LLM. Valid values: {valid}")

    try:
        result = YouTubeSummarizer(url, llm, language, model=model).run()
    except RuntimeError as exc:
        logging.error("Summarize failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

    return SummarizeResponse(
        video_title=result.video_title,
        video_url=result.video_url,
        llm_used=result.llm_used,
        language=result.language,
        transcript=result.transcript,
        summary=result.summary,
        time_stats=TimeStatsResponse(
            video_length_seconds=result.time_stats.video_length_seconds,
            video_length_minutes=result.time_stats.video_length_minutes,
            word_count=result.time_stats.word_count,
            reading_time_seconds=result.time_stats.reading_time_seconds,
            reading_time_minutes=result.time_stats.reading_time_minutes,
            time_saved_seconds=result.time_stats.time_saved_seconds,
            time_saved_minutes=result.time_stats.time_saved_minutes,
            percentage_saved=result.time_stats.percentage_saved,
        ),
    )


def run_chat(transcript: str, llm_value: str, history: list[ChatMessage], message: str, model: str | None = None) -> ChatResponse:
    llm = LLMOptionEnum.from_name(llm_value.upper())
    if llm is None:
        valid = [o["value"] for o in LLMOptionEnum.list_options()]
        raise HTTPException(status_code=422, detail=f"Unknown LLM. Valid values: {valid}")

    context = retrieve_relevant_chunks(transcript, message)
    system = f"Answer questions about the following video transcript excerpt.\n\nExcerpt:\n{context}"
    messages = [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": message})

    summarizer = Summarizer(llm, "english", model=model)
    reply = summarizer.client.chat_with_history(system, messages)
    if reply is None:
        raise HTTPException(status_code=500, detail="LLM returned no response.")
    return ChatResponse(reply=reply)

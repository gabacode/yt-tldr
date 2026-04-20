from pydantic import BaseModel


class SummarizeRequest(BaseModel):
    url: str
    llm: str
    language: str = "english"
    model: str | None = None


class TimeStatsResponse(BaseModel):
    video_length_seconds: float
    video_length_minutes: float
    word_count: int
    reading_time_seconds: float
    reading_time_minutes: float
    time_saved_seconds: float
    time_saved_minutes: float
    percentage_saved: float


class SummarizeResponse(BaseModel):
    video_title: str
    video_url: str
    llm_used: str
    language: str
    transcript: str
    summary: str
    time_stats: TimeStatsResponse


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    transcript: str
    llm: str
    history: list[ChatMessage] = []
    message: str
    model: str | None = None


class ChatResponse(BaseModel):
    reply: str


class ModelsResponse(BaseModel):
    models: list[str]


class LLMOption(BaseModel):
    name: str
    value: str


class LLMsResponse(BaseModel):
    llms: list[LLMOption]

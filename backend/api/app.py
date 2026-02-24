from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import ChatRequest, ChatResponse, LLMsResponse, ModelsResponse, SummarizeRequest, SummarizeResponse
from api.services import get_llms, get_models, run_chat, run_summarize

app = FastAPI(title="yt-tldr API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/llms", response_model=LLMsResponse)
def list_llms():
    return get_llms()


@app.get("/models", response_model=ModelsResponse)
def list_models(llm: str = Query(...)):
    return get_models(llm)


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    return run_summarize(request.url, request.llm, request.language, model=request.model)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return run_chat(request.transcript, request.llm, request.history, request.message, model=request.model)

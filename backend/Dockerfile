FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install "setuptools<70" wheel \
    && pip install --no-build-isolation openai-whisper==20240930 \
    && pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "server.py"]
